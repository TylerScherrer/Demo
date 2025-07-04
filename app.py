from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import pickle
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from pandas import Timestamp
from datetime import timedelta

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
    tokenizer.pad_token = tokenizer.eos_token  # Set pad token for batching

    if torch.cuda.is_available():
        phi_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            device_map="auto"
        )
    else:
        phi_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,  # Float16 saves memory even on CPU
            low_cpu_mem_usage=True,
            device_map={"": "cpu"}  # Force CPU
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

category_features = [
    col for col in df.columns
    if col.endswith("_Sales") and col != "Total_Sales" and col in df.columns
]


@app.route("/")
def home():
    return jsonify({"message": "🟢 ML Forecast API is running!"})

@app.route("/api/stores", methods=["GET"])
def get_stores():
    try:
        if df is None:
            print("❌ DataFrame is None")
            return jsonify({"error": "features.csv not loaded"}), 500

        print(f"✅ DataFrame loaded with columns: {list(df.columns)}")

        required_columns = ["Store Number", "City", "County"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return jsonify({"error": f"Missing columns: {missing_columns}"}), 500

        print("🔍 Filtering and deduplicating store info...")
        store_info = (
            df[["Store Number", "City", "County"]]
            .dropna()
            .drop_duplicates()
            .sort_values("Store Number")
            .to_dict(orient="records")
        )

        print(f"✅ Extracted {len(store_info)} unique store records.")
        return jsonify({"stores": store_info})

    except Exception as e:
        print(f"❌ Exception in /api/stores: {e}")
        return jsonify({"error": "Internal server error"}), 500






@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        print("🛠 Incoming prediction request data:", data)

        if not data or "store" not in data:
            return jsonify({"error": "Missing 'store' in request"}), 400

        store = int(data.get("store"))
        months = int(data.get("months", 4))  # default to 4 months



        if df is None or model is None:
            return jsonify({"error": "Model or dataset not available"}), 500

        store_df = df[df["Store Number"] == store].copy()
        if store_df.empty:
            return jsonify({"error": f"No data found for store {store}"}), 404

        timeline = []

        # Historical sales (last 6 weeks)
        # Convert date to datetime
        store_df['Date'] = pd.to_datetime(store_df['Date'])

        weekly_sales = store_df.groupby(pd.Grouper(key="Date", freq="MS"))["Total_Sales"].sum().reset_index()



        # Select last 6 weeks
        history_rows = weekly_sales.tail(6)

        for i, row in enumerate(history_rows.itertuples(), start=-6):
            timeline.append({
                "week": i,
                "type": "actual",
                "value": round(float(row.Total_Sales)),
                "month_start": row.Date.strftime("%Y-%m-%d"),
                "label": row.Date.strftime("%B %Y")  # e.g., "January 2021"
            })



        latest_row = store_df.iloc[-1:].copy()

        latest_date = latest_row["Date"].values[0]
        latest_week_start = pd.to_datetime(latest_date).replace(day=1)


        # Category Breakdown --

        # === Category Breakdown Proportions ===
        last_total = sum(latest_row[cat].values[0] for cat in category_features)
        category_shares = {
            cat.replace('_Sales', ''): (latest_row[cat].values[0] / last_total) if last_total > 0 else 0
            for cat in category_features
        }




        for col in model_features:
            if col not in latest_row.columns:
                latest_row[col] = 0

        lag_values = [latest_row[col].values[0] for col in ['Lag_1', 'Lag_2', 'Lag_3', 'Lag_12']]

        for i in range(1, months + 1):
            forecast_month_start = (latest_week_start + pd.DateOffset(months=i)).replace(day=1)
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

            category_breakdown = {
                cat: round(share * y, 2)
                for cat, share in category_shares.items()
                if share * y > 10 # optional filter to ignore tiny numbers 
            }

            timeline.append({
                "month": i,
                "type": "forecast",
                "value": round(float(y), 2),
                "lower": round(float(y) * 0.9, 2),
                "upper": round(float(y) * 1.1, 2),
                "category_breakdown": category_breakdown,
                "month_start": forecast_month_start.strftime("%Y-%m-%d"),
                "label": forecast_month_start.strftime("%B %Y")
            })


        print("📦 Final forecast timeline response:")
        for row in timeline:
            if row["type"] == "forecast":
                print(f"{row['label']} ➜ ${row['value']:.2f}")

                print("  Category Breakdown:", row.get("category_breakdown", "❌ Missing"))

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
        print("🧪 Raw /api/explain_forecast input:", timeline)

        if not timeline:
            print("⚠️ Timeline is missing or empty.")
            return jsonify({"error": "No forecast provided"}), 400

        forecast_part = [f for f in timeline if f["type"] == "forecast"]
        if not forecast_part:
            print("⚠️ No forecast entries found in timeline.")
            return jsonify({"summary": "No forecast data available for explanation."})

        prompt = (
            "Provide a concise and clear summary (without exercises or additional tasks) "
            "analyzing the following monthly liquor sales forecast for a store manager:\n\n"
            + "\n".join([f"{f['label']}: ${f['value']}" for f in forecast_part])
        )


        print("📤 Prompt to model:\n", prompt)

        inputs = tokenizer(prompt, return_tensors="pt", padding=True)
        input_ids = inputs["input_ids"]
        attention_mask = inputs["attention_mask"]

        # 💡 Check for NaNs or Infs
        if torch.isnan(input_ids).any() or torch.isinf(input_ids).any():
            print("❌ NaN or Inf detected in input_ids")
            return jsonify({"summary": "Input tensor invalid — NaN or Inf detected."})

        outputs = phi_model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=100,
            pad_token_id=tokenizer.eos_token_id,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95
        )

        try:
            decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
            print("📜 Decoded response:", repr(decoded))

            # Try to strip the prompt if present
            if decoded.startswith(prompt):
                explanation = decoded[len(prompt):].strip()
            else:
                explanation = decoded.strip()

            if not explanation or explanation.lower().startswith("exercise") or "graph" in explanation.lower():
                print("⚠️ Unusable explanation, fallback triggered.")
                explanation = "Sales are forecasted to decline over the next few weeks. Please monitor trends."

        except Exception as decode_err:
            print(f"❌ Decoding failed: {decode_err}")
            explanation = "Model produced an unreadable result."


        print("📬 AI Explanation output:", explanation)

        return jsonify({"summary": explanation or "The forecast suggests a trend, but no summary was returned."})

    except Exception as e:
        print(f"❌ Phi-1.5 inference error: {e}")
        return jsonify({"error": "Failed to generate explanation"}), 500







if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)