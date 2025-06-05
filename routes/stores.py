from flask import Blueprint, jsonify, current_app
import logging

stores_bp = Blueprint("stores", __name__)

@stores_bp.route("", methods=["GET"])
def get_stores():
    logging.info("🔥 /stores endpoint was hit!")
    df = current_app.config["df"]
    store_ids = sorted(df["Store Number"].unique())
    return jsonify({"stores": store_ids})
