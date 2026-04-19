import requests
from rich.console import Console
from dataclasses import dataclass, field
from typing import Any, Callable
import datetime
import getpass

@dataclass
class Agent:
    system_prompt: str = "You are an AI chatbot assistant for a software called MedPred.AI developed by Akshay Babu, you are an assistant/helper to the users that may use the App or the API to calculate their medical insurance expenses, predicted by MedPred.AI using their Age, BMI. use these values to give them advice on their health and how they must move on with their life."
    model: str = "qwen2.5-coder-3b-instruct"
    base_url: str = "http://127.0.0.1:1234/v1"
    api_key: str = field(default="NO_API_KEY", repr=False)
    contexts: dict[str, Callable[[], str]] = field(default_factory=dict)
    messages: list[dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self) -> None:
         self.base_url.rstrip("/")
         
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
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        r = requests.post(
            url,
            headers=headers,
            json={"model": self.model, "messages": prefix + self.messages},
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
        
        response = message.get("content") or ""
        self.messages.append({"role": "assistant", "content": response})
        return response

def main() -> None:
    agent = Agent(
        model="qwen2.5-coder-3b-instruct",
        system_prompt= "You are an AI chatbot assistant for a software called MedPred.AI developed by Akshay Babu, you are an assistant/helper to the users that may use the App or the API to calculate their medical insurance expenses, predicted by MedPred.AI using their Age, BMI. use these values to give them advice on their health and how they must move on with their life."    
    )
    
    @agent.context
    def time_user_context() -> str:
        return (
            f"Current date and time : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Current user : {getpass.getuser()}\n"
        )
    
    console = Console()
    
    console.print(f"[blue]Assistant: [/blue]Hello, I'm MedPred.AI. Please enter you age, bmi and I will predict your insurance in dollars, also feel free to ask questions!")
    
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
    