from flask import Blueprint, request, jsonify, current_app, make_response
import pandas as pd

seasonality_bp = Blueprint("seasonality", __name__)

@seasonality_bp.route("/seasonality", methods=["GET", "OPTIONS"])
def seasonality_analysis():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "https://calm-river-00759800f.6.azurestaticapps.net"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response, 200

    store_param = request.args.get("store", None)

    df = current_app.config["df"]
    if store_param:
        try:
            store_id = int(store_param)
        except ValueError:
            return jsonify({"error": "Invalid store ID"}), 400
        store_df = df[df["Store Number"] == store_id].copy()
        if store_df.empty:
            return jsonify({"error": f"Store {store_id} not found."}), 404
    else:
        store_df = df.copy()

    monthly_stats = (
        store_df.groupby("Month")["Total_Sales"]
        .agg(["mean", "std"])
        .reset_index()
        .sort_values("Month")
    )

    results = []
    for _, row in monthly_stats.iterrows():
        results.append({
            "month": int(row["Month"]),
            "avg_sales": float(row["mean"]),
            "std_sales": float(row["std"]) if not pd.isna(row["std"]) else 0.0
        })

    return jsonify({"seasonality": results})
