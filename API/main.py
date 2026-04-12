from fastapi import FastAPI
import pandas as pd

import MedPred as med

def get_data():
    age = med.age
    bmi = med.bmi
    ins = med.pred
    
    return age, bmi, ins

age, bmi, ins = get_data()

get_data()

print(age)
print(bmi)
print(ins)

