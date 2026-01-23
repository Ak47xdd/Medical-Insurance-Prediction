import pandas as pd 
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


df = pd.read_csv(r"C:\Portfolio-Projects\Medical-Insurance-Prediction\Data\insurance.csv")

df_1 = df.drop(columns= 'sex', axis = 1)
df_1 = df.drop(columns= 'region', axis = 1)
df_1 = df.drop(columns= 'smoker', axis = 1)

df_1['log_charges'] = np.log2(df_1['charges'])
df['log_charges'] = np.log2(df['charges'])
df_1['is_smoker'] = df['smoker'] == 'yes'

df.drop('smoker', axis =1, inplace = True)
df.drop('region', axis =1, inplace = True)
df.drop('sex', axis =1, inplace = True)

df_numrc = df_1[['age', 'bmi', 'children', 'charges', 'log_charges']]

smokers_df =df_1[df_1['is_smoker'] == True]

X = smokers_df[['age', 'bmi']]
y = smokers_df['log_charges']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

smoker_model = LinearRegression(fit_intercept= True)
smoker_model.fit(X_train, y_train)
smoker_model.coef_

y_pred = smoker_model.predict(X_train)

test_pred = smoker_model.predict(X_test)

mean_squared_error(y_test, test_pred)

class Predictor :

    def __init__(self, age, bmi):
        self.age = age
        self.bmi = bmi
        model_test = pd.DataFrame([self.age, self.bmi]).transpose()
        model_test.columns = ['age', 'bmi']
        self.new_pred = smoker_model.predict(model_test)
        self.new_pred = (np.exp2(self.new_pred))

    def __str__(self):
        return f"{float(self.new_pred.round(3)):,.2f}"
