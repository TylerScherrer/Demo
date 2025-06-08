from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import pickle

# === Initialize Flask App ===
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}}, supports_credentials=True)

# === Load Features CSV ===
FEATURES_PATH = os.path.join(os.path.dirname(__file__), "features.csv")
try:
    df = pd.read_csv(FEATURES_PATH)
    print(f"✅ Loaded features.csv with columns: {list(df.columns)}")
except Exception as e:
    print(f"❌ Could not load features.csv: {e}")
    df = None

# === Load Trained Model ===
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

# === Routes ===

@app.route("/")
def home():
    return jsonify({"message": "🟢 Flask backend is running!"})

@app.route("/api/hello")
def hello():
    return jsonify({"message": "Hello from Flask!"})

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
            print("❌ Model or dataset is not available")
            return jsonify({"error": "Model or dataset not available"}), 500

        store_df = df[df["Store Number"] == store].copy()
        print(f"🔍 Found {len(store_df)} rows for store {store}")

        if store_df.empty:
            return jsonify({"error": f"No data found for store {store}"}), 404

        # Use the last row — sorted by Date if available
        if "Date" in store_df.columns:
            latest_row = store_df.sort_values("Date").iloc[-1:]
        else:
            latest_row = store_df.iloc[-1:]
            print("⚠️ 'Date' column not found; using last row without sorting")

        # Repeat the row N times for the forecast
        future_df = pd.concat([latest_row] * weeks, ignore_index=True)

        # Fill in missing model features with default values
        for col in model_features:
            if col not in future_df.columns:
                print(f"⚠️ Missing feature '{col}' — filling with 0")
                future_df[col] = 0

        # Reorder to match expected input
        future_df = future_df[model_features]
        print(f"🧠 Predicting with features: {list(future_df.columns)}")

        # Run prediction
        preds = model.predict(future_df)
        print(f"📈 Raw predictions: {preds}")

        forecast = []
        for i, y in enumerate(preds, 1):
            forecast.append({
                "week": i,
                "predicted": round(float(y), 2),
                "lower": round(float(y * 0.9), 2),
                "upper": round(float(y * 1.1), 2)
            })

        print(f"✅ Returning forecast with {len(forecast)} items")
        return jsonify({"prediction": forecast})

    except Exception as e:
        print(f"❌ Exception in /api/predict: {e}")
        return jsonify({"error": "Internal server error"}), 500

# === Start Server ===
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
