from flask import Blueprint, jsonify, current_app
import logging

# Create blueprint
stores_bp = Blueprint("stores", __name__)

@stores_bp.route("/", methods=["GET"])  # ← add slash to match frontend

def get_stores():
    logging.info("🔥 /api/stores endpoint was hit!")
    print("🔍 Endpoint hit: /api/stores")

    df = current_app.config.get("df")

    if df is None:
        logging.error("❌ DataFrame not found in app config.")
        print("❌ df is None in app.config")
        return jsonify({"error": "Store data unavailable"}), 500

    print(f"✅ DataFrame loaded. Columns: {list(df.columns)}")
    if "Store Number" not in df.columns:
        logging.error("❌ 'Store Number' column missing from DataFrame.")
        print("❌ 'Store Number' column missing from DataFrame.")
        return jsonify({"error": "'Store Number' column missing"}), 500

    store_ids = sorted(df["Store Number"].unique())
    print(f"📦 Returning {len(store_ids)} store IDs.")

    return jsonify({"stores": store_ids})
