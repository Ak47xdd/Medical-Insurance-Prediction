import requests
from rich.console import Console
from dataclasses import dataclass, field
from typing import Any, Callable, Annotated, get_origin, get_args, Union, Final
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import requests
import os
import inspect
import json
import datetime
import getpass

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set")

@dataclass
class Tools:
    TOOL_SCHEMA_ATTR: Final[str] = "__tool_schema__"
    tools: dict[str, Callable[..., Any]] = field(default_factory=dict)
    
    @staticmethod
    def _annotation_to_schema(annotation: Any) -> dict[str, Any]:
        schema: dict[str, Any] = {"type": "string"}
        description: str | None = None
        origin = get_origin(annotation)
        
        if origin is Annotated:
            base_type, *meta = get_args(annotation)
            schema = Tools._annotation_to_schema(base_type)
            if meta:
                description = str(meta[0])
        elif annotation in (int, float):
            schema = {"type": "number"}
        elif annotation is bool:
            schema = {"type": "boolean"}
        elif annotation is str:
            schema = {"type": "string"}
        elif annotation is dict:
            schema = {"type": "object"}
        elif annotation is list:
            schema = {"type": "array"}
        elif origin is list:
            schema = {
                "type": "array",
                "items": Tools._annotation_to_schema(get_args(annotation)[0]),
            }
            
        elif origin is dict:
            schema = {
                "type": "object"
            }
        elif origin is Union:
            any_of = [
                Tools._annotation_to_schema(arg)
                for arg in get_args(annotation)
                if arg is not type(None)
            ]
            if any_of:
                schema = any_of[0]
                
        if description:
            schema["description"] = description
            
        return schema
    
    @classmethod
    def schema_for_callable(cls, func: Callable[..., Any]) -> dict[str, Any]:
        sig = inspect.signature(func)
        annotations = inspect.get_annotations(func)
        
        parameters: dict[str, Any] = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }
        
        for name, param in sig.parameters.items():
            annotation = annotations.get(name, inspect.Parameters.empty)
            
            if annotation is inspect.Parameter.empty:
                continue
            
            parameters["properties"][name] = cls._annotation_to_schema(annotation)
            
            if param.default is param.empty:
                parameters["required"].append(name)
                
        return {
            "type": "function",
            "function": {
                "name": func.__doc__ or "No desc provided.",
                "parameters": parameters,
                "strict": True,
            },
        }
            
    def get_schemas(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for fn in self.tools.values():
            s = getattr(fn, self.TOOL_SCHEMA_ATTR, None)
            if s is not None:
                out.append(s)
        return out
    
    def register(self, func: Callable[..., Any]) -> Callable[..., Any]:
        if getattr(func, self.TOOL_SCHEMA_ATTR, None) is None:
            setattr(func, self.TOOL_SCHEMA_ATTR, self.schema_for_callable(func))
        self.tools[func.__name__] = func
        return func
    
    def execute(self, tool_call: dict[str, Any]) -> dict[str, Any]:
        fn_payload = tool_call.get("function") or {}
        fn_name = fn_payload.get("name")
        fn = self.tools.get(fn_name) if fn_name else None
        
        if not fn:
            return {"error": f"Tool '{fn_name}' not found"}
        
        try:
            args = json.loads(fn_payload.get("arguments") or "{}")
            result = fn(**args)
            return result if isinstance(result, dict) else {"result": result}
        except KeyboardInterrupt:
            raise
        except Exception as e:
            return {"error": str(e)}
            

@dataclass
class Agent:
    system_prompt: str = "You are an AI chatbot assistant for a software called MedPred.AI developed by Akshay Babu, you are an assistant/helper to the users that may use the App or the API to calculate their medical insurance expenses, predicted by MedPred.AI using their Age, BMI. use these values to give them advice on their health and how they must move on with their life. keep the responses short and consise"
    model: str = "openai/gpt-oss-120b"
    base_url: str = "https://api.groq.com/openai/v1"
    api_key: str = GROQ_API_KEY
    tools: Tools = field(default_factory=Tools)
    contexts: dict[str, Callable[[], str]] = field(default_factory=dict)
    messages: list[dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self) -> None:
         self.base_url = self.base_url.rstrip("/")
         
    def context(self, func: Callable[[], str]) -> Callable[[], str]:
        self.contexts[func.__name__] = func
        return func
         
    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})
        
        context_content = "\n\n".join(
            f"<context>\n<{n}>{fn()}</{n}>\n</context>"
            for n, fn in self.contexts.items()
        )
        
        prefix: list[dict[str, Any]] = [
            {"role": "system", "content" : self.system_prompt},
            {"role": "system", "content" : context_content},
        ]
        
        while True:
            api_kwargs ={
                "model": self.model,
                "messages": prefix + self.messages,
            }
            
            tool_schemas = self.tools.get_schemas()
            if tool_schemas:
                api_kwargs["tools"] = tool_schemas
                
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            r = requests.post(
                url,
                headers=headers,
                json=api_kwargs,
                timeout=300,
            )
            r.raise_for_status()
            data = r.json()
            choices = data.get("choices")
            
            if not choices:
                raise RuntimeError("Model response missing choices")
            
            message = choices[0].get("message")
            if message is None:
                raise RuntimeError("Model response missing message")
            
            tool_calls = message.get("tool_calls") or []
            self.messages.append({
                "role": "assistant",
                "content": message.get("content"),
                "tool_calls": [
                    {
                        "id": tc.get("id"),
                        "type": tc.get("type"),
                        "function": {
                            "name": (tc.get("function") or {}).get("name"),
                            "arguments": (tc.get("function") or {}).get("arguments"),
                        },
                    }
                    for tc in tool_calls
                ],
            })
            
            if not tool_calls:
                return message.get("content") or ""
            
            for tool_call in tool_calls:
                result = self.tools.execute(tool_call)
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id"),
                        "content": json.dumps(result),
                    }
                )

def main() -> None:
    agent = Agent(
        model="openai/gpt-oss-120b",
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY,
        system_prompt= "You are an AI chatbot assistant for a software called MedPred.AI developed by Akshay Babu, you are an assistant/helper to the users that may use the App or the API to calculate their medical insurance expenses, predicted by MedPred.AI using their Age, BMI. use these values to give them advice on their health and how they must move on with their life. keep the responses short and consise"    
    )

    @agent.context
    def time_user_context() -> str:
        return (
            f"Current date and time : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Current user : {getpass.getuser()}\n"
        )
        
    @agent.context
    def user_info_context() -> str:
        df = pd.read_csv(r"C:\Portfolio-Projects\Medical-Insurance-Prediction\API\new_data.csv")
        return (
            f"Age of the user : {df['age'].iloc[-1]}"
            f"BMI of the user : {df['bmi'].iloc[-1]}"
            f"Predicted Insurance : {df['charges'].iloc[-1]:.4f}"
        )
    
    console = Console()
    
    console.print(f"[blue]MedPrd.AI: [/blue]Hello, I'm MedPred.AI. Please enter you age, bmi in the MedPred.AI App and I will predict your insurance in dollars, also feel free to ask questions!")
    
    while True :
        console.print("[green]You:[/green] ", end="")
        user_input = console.input()
        
        if user_input.strip().lower() in {"quit", "exit"}:
            console.print("[dim]Goodbye![/dim]")
            return
        
        with console.status("[dim]Thinking...[/dim]", spinner="arc"):
            response = agent.chat(user_input).strip()
            console.print(f"[blue]MedPrd.AI:[/blue] {response}")
    
if __name__ == "__main__":
    main()
    