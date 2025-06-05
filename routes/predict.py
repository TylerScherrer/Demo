from flask import Blueprint, request, jsonify, current_app
import numpy as np
import logging

# Initialize blueprint for predict
predict_bp = Blueprint("predict", __name__)

@predict_bp.route("", methods=["POST"], strict_slashes=False)
def predict_route():
    """
    POST /predict
    Expects JSON payload:
      { "store": <int>, "weeks": <int> }
    Returns JSON:
      { "prediction": [ { "predicted": float, "upper": float, "lower": float }, ... ],
        "total": float }
    """
    # Debug incoming request
    logging.debug("[predict] Incoming JSON: %s", request.get_json())
    data = request.get_json(silent=True) or {}

    # Validate and parse parameters
    store = data.get("store")
    weeks = data.get("weeks", 4)
    try:
        store = int(store)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing 'store' parameter"}), 400
    try:
        weeks = int(weeks)
    except (TypeError, ValueError):
        weeks = 4

    # Access data and model from app config
    df = current_app.config.get("df")
    model = current_app.config.get("model")
    features = current_app.config.get("model_features", [])
    avg_mae = current_app.config.get("AVG_MAE", 0)

    # Filter for the specified store
    store_df = df[df["Store Number"] == store].sort_values(by=["Year", "Month"])
    if store_df.empty:
        return jsonify({"error": f"Store {store} not found."}), 404

    # Start from the last available record
    current_row = store_df.iloc[-1].copy()
    month = int(current_row.get("Month", 1))
    predictions = []

    for _ in range(weeks):
        # Prepare feature vector
        X = current_row[features].values.reshape(1, -1)
        pred = float(model.predict(X)[0])
        upper = pred + avg_mae
        lower = max(pred - avg_mae, 0)

        predictions.append({"predicted": pred, "upper": upper, "lower": lower})

        # Shift lag features
        current_row["Lag_3"] = current_row["Lag_2"]
        current_row["Lag_2"] = current_row["Lag_1"]
        current_row["Lag_1"] = pred

        # Advance month and year
        month += 1
        if month > 12:
            month = 1
            current_row["Year"] = current_row.get("Year", 0) + 1
        current_row["Month"] = float(month)
        current_row["Month_sin"] = np.sin(2 * np.pi * month / 12)
        current_row["Month_cos"] = np.cos(2 * np.pi * month / 12)

        # Recompute rolling statistics and trend
        lags = [current_row["Lag_1"], current_row["Lag_2"], current_row["Lag_3"]]
        current_row["rolling_mean_3"] = np.mean(lags)
        current_row["rolling_std_3"] = np.std(lags)
        current_row["rolling_mean_6"] = np.mean(lags + [current_row["rolling_mean_3"]] * 3)
        current_row["rolling_trend"] = current_row["rolling_mean_3"] - current_row["rolling_mean_6"]
        current_row["sales_to_avg_ratio"] = pred / (current_row["rolling_mean_3"] + 1e-6)

    # Round and assemble response
    total = sum(item["predicted"] for item in predictions)
    results = [
        {"predicted": round(item["predicted"], 2),
         "upper": round(item["upper"], 2),
         "lower": round(item["lower"], 2)}
        for item in predictions
    ]

    return jsonify({"prediction": results, "total": round(total, 2)})