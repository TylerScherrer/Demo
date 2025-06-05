import os
import logging
from dotenv import load_dotenv

# 1) Load .env before anything else
load_dotenv()   # ← now OPENAI_API_KEY (and any other vars) are in os.environ

from flask import Flask
from flask_cors import CORS

# Blueprints (now that env is loaded, they’ll pick up OPENAI_API_KEY)
from routes.chat import chat_bp
from routes.stores import stores_bp
from routes.metrics import metrics_bp
from routes.compare import compare_bp
from routes.predict import predict_bp
from routes.seasonality import seasonality_bp
from routes.feature_importance import feature_importance_bp
from routes.ai_summary import ai_summary_bp
from routes.ai_feature_importance import ai_feature_importance_bp

import urllib.request
import pickle
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s: %(message)s')

# === Azure Blob SAS URLs ===
MODEL_URL = "https://mlstoragegroup.blob.core.windows.net/ml-artifacts/model.pkl?sp=r&st=2025-04-16T00:54:37Z&se=2026-01-16T09:54:37Z&spr=https&sv=2024-11-04&sr=b&sig=9ui%2F6DONK0mcGhTwME0WFps93%2FytZnO%2BPsDIEIozxzQ%3D"
FEATURES_URL = "https://mlstoragegroup.blob.core.windows.net/ml-artifacts/features.csv?sp=r&st=2025-04-16T00:54:11Z&se=2025-12-01T09:54:11Z&spr=https&sv=2024-11-04&sr=b&sig=pMhMY2AmblthZe9UxP7AEPOU5A0DsFu2VF8kcubGxoU%3D"


# === Local Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "features.csv")

# === Download if missing ===
if not os.path.exists(MODEL_PATH):
    print("📦 Downloading model…")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
if not os.path.exists(FEATURES_PATH):
    print("📊 Downloading features…")
    urllib.request.urlretrieve(FEATURES_URL, FEATURES_PATH)

# === Load model & data ===
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)
df = pd.read_csv(FEATURES_PATH)

# === Feature Engineering ===
if 'Profit_Margin' not in df.columns:
    if 'State Bottle Retail' in df.columns and 'State Bottle Cost' in df.columns:
        df['Profit_Margin'] = (df['State Bottle Retail'] - df['State Bottle Cost']) / df['State Bottle Retail']
    else:
        df['Profit_Margin'] = np.nan

if 'Is_Promotion_Month' not in df.columns:
    if 'Month' not in df.columns and 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df['Month'] = df['Date'].dt.month
    df['Is_Promotion_Month'] = df['Month'].isin([11, 12]).astype(int)

if 'Average_Price' not in df.columns:
    if 'Sale (Dollars)' in df.columns and 'Bottles Sold' in df.columns:
        df['Average_Price'] = df['Sale (Dollars)'] / df['Bottles Sold'].replace(0, np.nan)
        df['Average_Price'] = df['Average_Price'].fillna(0)
    else:
        df['Average_Price'] = np.nan

# === Constants ===
AVG_MAE = 5000
model_features = [
    'Lag_1', 'Lag_2', 'Lag_3', 'Lag_12',
    'Month_sin', 'Month_cos',
    'store_mean_sales', 'store_std_sales',
    'rolling_mean_3', 'rolling_std_3',
    'rolling_mean_6', 'rolling_trend', 'sales_to_avg_ratio',
    'Profit_Margin', 'Is_Promotion_Month', 'Average_Price'
]

# === Create Flask App ===
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://calm-river-00759800f.6.azurestaticapps.net"}},
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])




# === App Configuration ===
app.config["df"] = df
app.config["model"] = model
app.config["AVG_MAE"] = AVG_MAE
app.config["model_features"] = model_features

# === Health Check ===
@app.route("/")
def index():
    return "🚀 ML Forecast API is live and working!"

# === Register Blueprints with prefixes ===
from routes.stores import stores_bp
from routes.metrics import metrics_bp
from routes.compare import compare_bp
from routes.predict import predict_bp
from routes.seasonality import seasonality_bp
from routes.feature_importance import feature_importance_bp
from routes.ai_summary import ai_summary_bp
from routes.ai_feature_importance import ai_feature_importance_bp

# === Register blueprints ===
app.register_blueprint(chat_bp, url_prefix="/api")
app.register_blueprint(stores_bp, url_prefix="/stores")
app.register_blueprint(metrics_bp, url_prefix="/metrics")
app.register_blueprint(compare_bp, url_prefix="/compare")
app.register_blueprint(predict_bp, url_prefix="/predict")
app.register_blueprint(seasonality_bp, url_prefix="/analysis")
app.register_blueprint(feature_importance_bp, url_prefix="/feature_importance")
app.register_blueprint(ai_summary_bp, url_prefix="/ai-summary")
app.register_blueprint(ai_feature_importance_bp, url_prefix="/ai_feature_importance")

# === Azure Compatibility ===
application = app

# === Run locally ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🌐 Starting app on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port)