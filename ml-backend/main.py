# === File: main.py ===
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os
import pickle
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from routes import register_routes

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}}, supports_credentials=True)

# === Load Core Data ===
base_path = os.path.dirname(__file__)
df_path = os.path.join(base_path, "features.csv")
model_path = os.path.join(base_path, "model.pkl")

# Load CSV and model
df = pd.read_csv(df_path)
with open(model_path, "rb") as f:
    model = pickle.load(f)

# Define model features
model_features = [
    'Lag_1', 'Lag_2', 'Lag_3', 'Rolling_3', 'Rolling_6', 'Rolling_12',
    'Rolling_Trend', 'Month', 'Quarter', 'IsYearStart', 'IsYearEnd',
    'AvgPricePerBottle', 'MarginRatio', 'UniqueProductsSold',
    'Bottles Sold', 'IsHolidayMonth'
]

# Category columns
category_features = [
    col for col in df.columns if col.endswith("_Sales") and col != "Total_Sales"
]

# Load LLM
model_name = "microsoft/phi-1_5"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

if torch.cuda.is_available():
    phi_model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16, low_cpu_mem_usage=True, device_map="auto"
    )
else:
    phi_model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16, low_cpu_mem_usage=True, device_map={"": "cpu"}
    )

# Register all routes
shared_context = {
    "df": df,
    "model": model,
    "model_features": model_features,
    "category_features": category_features,
    "phi_model": phi_model,
    "tokenizer": tokenizer
}
register_routes(app, shared_context)

@app.route("/")
def home():
    return jsonify({"message": "🟢 ML Forecast API is modular and running!"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
