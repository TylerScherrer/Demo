from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import pickle
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

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

# === Load Phi-1.5 with memory-safe config ===
try:
    model_name = "microsoft/phi-1_5"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token  # Ensure pad_token is set

    phi_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto"
    )
    print("✅ Phi-1.5 model loaded with memory-safe config")
except Exception as e:
    print(f"❌ Failed to load Phi-1.5: {e}")
    phi_model = None
    tokenizer = None

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
    return jsonify({"stores": sorted(df["Store Number"].unique())})

@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        store = int(data.get("store"))
        weeks = int(data.get("weeks", 4))

        if df is None or model is None:
            return jsonify({"error": "Model or dataset not available"}), 500

        store_df = df[df["Store Number"] == store].copy()
        if store_df.empty:
            return jsonify({"error": f"No data found for store {store}"}), 404

        timeline = []

        # Historical sales (last 6 weeks)
        history_rows = store_df.iloc[-6:]
        for i, row in enumerate(history_rows.itertuples(), start=-6):
            timeline.append({
                "week": i,
                "type": "actual",
                "value": round(float(row.Total_Sales))
            })

        latest_row = store_df.iloc[-1:].copy()
        for col in model_features:
            if col not in latest_row.columns:
                latest_row[col] = 0

        lag_values = [latest_row[col].values[0] for col in ['Lag_1', 'Lag_2', 'Lag_3', 'Lag_12']]

        for week in range(1, weeks + 1):
            temp = latest_row.copy()
            temp['Lag_1'] = lag_values[-1]
            temp['Lag_2'] = lag_values[-2] if len(lag_values) > 1 else lag_values[-1]
            temp['Lag_3'] = lag_values[-3] if len(lag_values) > 2 else lag_values[-1]
            temp['Lag_12'] = lag_values[-12] if len(lag_values) > 11 else lag_values[0]

            for col in model_features:
                if col not in temp.columns:
                    temp[col] = 0
            temp = temp[model_features]

            y = model.predict(temp)[0]
            lag_values.append(y)

            timeline.append({
                "week": week,
                "type": "forecast",
                "value": round(float(y), 2),
                "lower": round(float(y) * 0.9, 2),
                "upper": round(float(y) * 1.1, 2)
            })

        return jsonify({"timeline": timeline})

    except Exception as e:
        print(f"❌ Exception in /api/predict: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/explain_forecast", methods=["POST"])
def explain_forecast():
    if not phi_model or not tokenizer:
        return jsonify({"error": "Phi-1.5 model not available"}), 500

    try:
        data = request.get_json()
        timeline = data.get("timeline")

        print("🧪 Raw /api/explain_forecast input:", timeline)  # 🔍 Log timeline

        if not timeline:
            print("⚠️ Timeline is missing or empty.")
            return jsonify({"error": "No forecast provided"}), 400

        forecast_part = [f for f in timeline if f["type"] == "forecast"]
        if not forecast_part:
            print("⚠️ No forecast entries found in timeline.")
            return jsonify({"summary": "No forecast data available for explanation."})

        prompt = (
            "Analyze the following liquor sales forecast and explain the trend to a beginner:\n\n"
            + "\n".join([f"Week {f['week']}: {f['value']}" for f in forecast_part])
        )

        print("📤 Prompt to model:\n", prompt)  # 🔍 Log prompt

        inputs = tokenizer(prompt, return_tensors="pt", padding=True)
        outputs = phi_model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=120,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95
        )

        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        explanation = decoded[len(prompt):].strip() if decoded.startswith(prompt) else decoded.strip()

        print("📬 AI Explanation output:", explanation)  # 🔍 Log AI result

        return jsonify({"summary": explanation or "The forecast suggests a trend, but no summary was returned."})

    except Exception as e:
        print(f"❌ Phi-1.5 inference error: {e}")
        return jsonify({"error": "Failed to generate explanation"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
