from flask import Blueprint, request, jsonify, current_app, make_response
from sklearn.metrics import mean_absolute_error, mean_squared_error
import math

metrics_bp = Blueprint("metrics", __name__)

@metrics_bp.route("", methods=["GET", "OPTIONS"])
def get_metrics():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "https://calm-river-00759800f.6.azurestaticapps.net"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response, 200

    df = current_app.config["df"]
    model = current_app.config["model"]
    model_features = current_app.config["model_features"]

    test_data = df.tail(200).copy()
    X_test = test_data[model_features]
    y_test = test_data["Total_Sales"]

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = math.sqrt(mse)

    return jsonify({
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2)
    })
