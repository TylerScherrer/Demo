from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os
import pickle
from routes import register_routes
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}}, supports_credentials=True)

# === Load Core Data ===
base_path = os.path.dirname(__file__)
df_path = os.path.join(base_path, "features.csv")
model_path = os.path.join(base_path, "model.pkl")

df = pd.read_csv(df_path)
with open(model_path, "rb") as f:
    model = pickle.load(f)

model_features = [
    'Lag_1', 'Lag_2', 'Lag_3', 'Rolling_3', 'Rolling_6', 'Rolling_12',
    'Rolling_Trend', 'Month', 'Quarter', 'IsYearStart', 'IsYearEnd',
    'AvgPricePerBottle', 'MarginRatio', 'UniqueProductsSold',
    'Bottles Sold', 'IsHolidayMonth'
]

category_features = [
    col for col in df.columns if col.endswith("_Sales") and col != "Total_Sales"
]

shared_context = {
    "df": df,
    "model": model,
    "model_features": model_features,
    "category_features": category_features,
}

# ✅ All routes now included here
register_routes(app, shared_context)
for rule in app.url_map.iter_rules():
    print(f"🔗 Registered route: {rule} --> methods: {rule.methods}")

@app.route("/")
def home():
    return jsonify({"message": "🟢 ML Forecast API is modular and running!"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
