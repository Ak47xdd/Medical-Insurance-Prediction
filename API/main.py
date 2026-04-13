from fastapi import FastAPI
from fastmcp import FastMCP
import pandas as pd

import MedPred as med

app = FastAPI(title="Database Management API - MedPred.AI")

# def get_data():
#     age = med.age_data
#     bmi = med.bmi_data
#     ins = med.ins_data

#     return age, bmi, ins

@app.post("/data")
def get_val():
    age, bmi, ins = med.get_data()

    pred_val = ins
    pred_val = [round(x, 4) for x in pred_val]

    # print(age)
    # print(bmi)
    # print(pred_val)

    rows = []
    for a, b, c in zip(age, bmi, pred_val):
        rows.append({'age': a, 'bmi': b, 'charges': c})
        
    new_data = pd.DataFrame(rows)

    new_data.to_csv("new_data.csv", mode='a', index=False, header=False)

# get_val()