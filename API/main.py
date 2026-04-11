from fastapi import FastAPI
import fastmcp
import pandas as pd

import MedPred as med

app = FastAPI(title="Realtime Database API")

def get_data():
    age = med.age
    bmi = med.bmi
    ins = med.pred
    print(age)
    print(bmi)
    print(ins)
    
get_data()