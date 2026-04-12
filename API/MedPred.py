import tkinter as tk
from tkinter import *
import Insurance as ins
import time

root = tk.Tk()

root.title("Medical Insurance Predictor")

root.iconbitmap(r"C:\Portfolio-Projects\Medical-Insurance-Prediction\App Source Files\MedPred.ico")

label_sub = Label(root, text='Predict Your Medical Insurance')
label_fields = Label(root, text= 'Enter the given fields')
label_age = Label(root, text='Enter the age of the patient :      $')
label_bmi = Label(root, text='Enter the BMI of the patient :      $')

label_sub.grid(row=0, column=1)
label_fields.grid(row=1, column=1)
label_age.grid(row=2, column=0)
label_bmi.grid(row=3, column=0)

str_var1 = tk.StringVar()

str_var2 = tk.StringVar()

global e1_age 
e1_age = Entry(root, textvariable=str_var1)
e1_age.grid(row=2,column=1)

global e2_bmi 
e2_bmi= Entry(root, textvariable=str_var2)
e2_bmi.grid(row=3,column=1)

error_label = None

# def on_resize(event):
    # """
    # Callback function to get and print the new width and height of the window.
    # use only if you want window data!
    # """
#     width = event.width
#     height = event.height                                                         # current = Width=573, Height=152
#     print(f"Window resized to: Width={width}, Height={height}")

# root.bind("<Configure>", on_resize)

def get_age_bmi() :
    global age 
    age = int(e1_age.get())
    
    global bmi 
    bmi = float(e2_bmi.get())
    
    if age > 120 or bmi > 210:
        raise ValueError("The given Age or BMI is not humanly possible!.")
    
    elif bmi == 0:
        raise ValueError("No one in this world has BMI 0.")
    
    if age < 0 or bmi < 0:
        raise ValueError("Age and BMI must be positive numbers.")
    
    return age, bmi
    
def predict() :
    global pred 
    pred = ins.Predictor(age=age, bmi=bmi)
    
    return pred

def on_click() :
    global error_label
    if error_label:
        error_label.destroy()
        error_label = None
    try:
        if not e1_age.get().strip() or not e2_bmi.get().strip():
            raise ValueError("Please enter values for both age and BMI.")
        
        get_age_bmi()
        
        clicked = Label(root, text="Predicting...")
        clicked.grid(row=5, column=3)
        start_time = time.time()
        
        predict()
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        clicked.destroy()
        
        label_output = Label(root, text=f'Insurance : ${predict()}')
        label_output.grid(row=4,column=1)
        label_time = Label(root, text=f'Time taken: {elapsed_time:.2f} seconds')
        label_time.grid(row=6, column=3)
        
        # e1_age.delete(0, END)
        # e2_bmi.delete(0, END)
        
    except Exception as e:
        error_label = Label(root, text=f"Error: {str(e)}")
        error_label.grid(row=7, column=1)


btn = Button(root, text= "Predict", command=on_click)


btn.grid(row=4, column=3)  
root.mainloop()
