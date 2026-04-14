from fastapi import FastAPI
from fastmcp import FastMCP
import pandas as pd
from pydantic import BaseModel
import os

app = FastAPI(title="Database Management API - MedPred.AI")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "new_data.csv")

class PatientEntry(BaseModel) :
    age : int
    bmi : float
    charges : float

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
