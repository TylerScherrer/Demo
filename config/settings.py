import pandas as pd
import numpy as np
import pickle

# Load model & data once here
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

df = pd.read_csv("features.csv")

# Ensure Actionable Features Exist
if 'Profit_Margin' not in df.columns:
    if 'State Bottle Retail' in df.columns and 'State Bottle Cost' in df.columns:
        df['Profit_Margin'] = (df['State Bottle Retail'] - df['State Bottle Cost']) / df['State Bottle Retail']
    else:
        df['Profit_Margin'] = np.nan

if 'Is_Promotion_Month' not in df.columns:
    if 'Month' not in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df['Month'] = df['Date'].dt.month
    df['Is_Promotion_Month'] = df['Month'].isin([11, 12]).astype(int)

if 'Average_Price' not in df.columns:
    if 'Sale (Dollars)' in df.columns and 'Bottles Sold' in df.columns:
        df['Average_Price'] = df['Sale (Dollars)'] / df['Bottles Sold'].replace(0, np.nan)
        df['Average_Price'] = df['Average_Price'].fillna(0)
    else:
        df['Average_Price'] = np.nan

AVG_MAE = 5000

# Model features
model_features = [
    'Lag_1', 'Lag_2', 'Lag_3', 'Lag_12',
    'Month_sin', 'Month_cos',
    'store_mean_sales', 'store_std_sales',
    'rolling_mean_3', 'rolling_std_3',
    'rolling_mean_6', 'rolling_trend', 'sales_to_avg_ratio',
    'Profit_Margin', 'Is_Promotion_Month', 'Average_Price'
]
