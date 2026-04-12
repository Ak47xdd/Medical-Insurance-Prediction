from fastapi import FastAPI
import pandas as pd

import MedPred as med

def get_data():
    age = med.age_data
    bmi = med.bmi_data
    ins = med.ins_data
    
    return age, bmi, ins

age, bmi, ins = get_data()

get_data()

pred_val = ins

print(age)
print(bmi)
print([round(x, 4) for x in pred_val])
