from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os

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
        return jsonify({"error": "'Store Number' column is missing"}), 500

    stores = sorted(df["Store Number"].unique())
    return jsonify({"stores": stores})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
