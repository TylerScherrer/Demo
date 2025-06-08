from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import pickle

# === Initialize Flask App ===
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}}, supports_credentials=True)

# === Load features.csv ===
FEATURES_PATH = os.path.join(os.path.dirname(__file__), "features.csv")
try:
    df = pd.read_csv(FEATURES_PATH)
    print(f"✅ Loaded features.csv with columns: {list(df.columns)}")
except Exception as e:
    print(f"❌ Could not load features.csv: {e}")
    df = None

# === Load model.pkl ===
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Could not load model.pkl: {e}")
    model = None

# === Define model-required input features ===
model_features = [
    'Lag_1', 'Lag_2', 'Lag_3', 'Lag_12',
    'Month_sin', 'Month_cos',
    'store_mean_sales', 'store_std_sales',
    'rolling_mean_3', 'rolling_std_3',
    'rolling_mean_6', 'rolling_trend', 'sales_to_avg_ratio',
    'Profit_Margin', 'Is_Promotion_Month', 'Average_Price'
]

@app.route("/")
def home():
    return jsonify({"message": "🟢 ML Forecast API is running!"})

@app.route("/api/stores", methods=["GET"])
def get_stores():
    if df is None:
        return jsonify({"error": "features.csv not loaded"}), 500

    if "Store Number" not in df.columns:
        return jsonify({"error": "'Store Number' column missing"}), 500

    store_ids = sorted(df["Store Number"].unique())
    return jsonify({"stores": store_ids})

@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        print(f"📥 Received predict request: {data}")

        store = int(data.get("store"))
        weeks = int(data.get("weeks", 4))

        if df is None or model is None:
            return jsonify({"error": "Model or dataset not available"}), 500

        store_df = df[df["Store Number"] == store].copy()
        if store_df.empty:
            return jsonify({"error": f"No data found for store {store}"}), 404

        # Use last row as base
        if "Date" in store_df.columns:
            latest_row = store_df.sort_values("Date").iloc[-1:].copy()
        else:
            latest_row = store_df.iloc[-1:].copy()

        # Ensure missing features are filled
        for col in model_features:
            if col not in latest_row.columns:
                latest_row[col] = 0

        forecast = []
        lag_values = [
            latest_row['Lag_1'].values[0],
            latest_row['Lag_2'].values[0],
            latest_row['Lag_3'].values[0],
            latest_row['Lag_12'].values[0]
        ]

        for week in range(1, weeks + 1):
            temp = latest_row.copy()

            # Update lag features
            temp['Lag_1'] = lag_values[-1]  # most recent prediction
            temp['Lag_2'] = lag_values[-2] if len(lag_values) > 1 else lag_values[-1]
            temp['Lag_3'] = lag_values[-3] if len(lag_values) > 2 else lag_values[-1]
            temp['Lag_12'] = lag_values[-12] if len(lag_values) > 11 else lag_values[0]

            # You can also update Month_cos/sin, rolling features, etc. here if needed

            # Ensure column order and defaults
            for col in model_features:
                if col not in temp.columns:
                    temp[col] = 0
            temp = temp[model_features]

            # Predict
            y = model.predict(temp)[0]
            lag_values.append(y)

            forecast.append({
                "week": week,
                "predicted": round(float(y), 2),
                "lower": round(float(y) * 0.9, 2),
                "upper": round(float(y) * 1.1, 2)
            })

        print(f"✅ Forecast complete for store {store}")
        return jsonify({"prediction": forecast})

    except Exception as e:
        print(f"❌ Exception in /api/predict: {e}")
        return jsonify({"error": "Internal server error"}), 500

# === Run Server ===
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
