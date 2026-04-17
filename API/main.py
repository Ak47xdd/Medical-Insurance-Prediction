from fastapi import FastAPI
from fastmcp import FastMCP
import pandas as pd
from pydantic import BaseModel
import os

import MedPred as med
import Insurance as ins

app = FastAPI(title="Database Management API - MedPred.AI")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "new_data.csv")

class PatientEntry(BaseModel) :
    age : int
    bmi : float
    charges : float
    
@app.post("/predict/")
async def predict(age : int, bmi : float) :
    pred_api = ins.Predictor(age=age, bmi=bmi).new_pred
    preds = round(pred_api, 4)
    
    data = [
        age,
        bmi,
        preds
    ]
    
    df = pd.DataFrame(data).transpose()
    
    if os.path.exists(CSV_PATH) :
        df.to_csv(CSV_PATH, mode="a", header=False, index=False)
    else :
        df.to_csv(CSV_PATH, mode="w", header=True, index=False)
        
    return pred_api

@app.post("/data")
def get_val(entry : PatientEntry):
    new_row = pd.DataFrame([entry.model_dump()])
    
    if os.path.exists(CSV_PATH) :
        new_row.to_csv(CSV_PATH, mode="a", header=False, index=False)
    else :
        new_row.to_csv(CSV_PATH, mode="w", header=True, index=False)
        
    return {"status" : "success", "message" : "Entry Added."}
    
@app.get("/entries")
def entries() :
    if not os.path.exists(CSV_PATH) :
        return {"data" : []}
    df = pd.read_csv(CSV_PATH)
    return {"data" : df.to_dict(orient="records")}

@app.get("/")
def root():
    return {"message": "Backend MedPred API running!"}