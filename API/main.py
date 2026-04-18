from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP
import pandas as pd
from pydantic import BaseModel
import os

import Insurance as ins
import MedPred as med

app = FastAPI(title="Database Management API - MedPred.AI")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "new_data.csv")

class PatientEntry(BaseModel):
    age: int
    bmi: float
    charges: float

@app.post("/predict/")
async def predict(age: int, bmi: float) -> float:
    try:
        pred_api = ins.Predictor(age=age, bmi=bmi).new_pred
        preds = round(pred_api, 4)
        
        data = [
            age,
            bmi,
            preds
        ]
        
        head = [
            "age",
            "bmi",
            "charges"
        ]
        
        df = pd.DataFrame(data).transpose()
        
        if os.path.exists(CSV_PATH):
            df.to_csv(CSV_PATH, mode="a", header=False, index=False)
        else:
            df.to_csv(CSV_PATH, mode="w", header=head, index=False)

        return preds
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data")
def get_val(entry: PatientEntry) -> dict:
    try:
        new_row = pd.DataFrame([entry.model_dump()])
        
        if os.path.exists(CSV_PATH):
            new_row.to_csv(CSV_PATH, mode="a", header=False, index=False)
        else:
            new_row.to_csv(CSV_PATH, mode="w", header=True, index=False)
        
        return {"status": "success", "message": "Entry Added."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/entries")
def entries() -> dict:
    try:
        if not os.path.exists(CSV_PATH):
            return {"data": []}

        df = pd.read_csv(CSV_PATH)
        return {"data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Backend MedPred API running!"}
