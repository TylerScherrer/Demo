from flask import Blueprint, request, jsonify, current_app, make_response
import pandas as pd

feature_importance_bp = Blueprint("feature_importance", __name__)

@feature_importance_bp.route("", methods=["GET", "OPTIONS"])
def get_feature_importance():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "https://calm-river-00759800f.6.azurestaticapps.net"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response, 200

    model = current_app.config["model"]
    model_features = current_app.config["model_features"]

    if not hasattr(model, "feature_importances_"):
        return jsonify({"error": "Model does not provide feature_importances_"}), 400

    importances = model.feature_importances_
    if len(importances) != len(model_features):
        return jsonify({"error": "Mismatch between model_features and feature_importances_ length"}), 500

    df_imp = pd.DataFrame({
        "feature": model_features,
        "importance": importances
    }).sort_values(by="importance", ascending=False)

    actionable_features = {"Profit_Margin", "Is_Promotion_Month", "Average_Price"}
    df_actionable = df_imp[df_imp["feature"].isin(actionable_features)]
    df_conceptual = df_imp[~df_imp["feature"].isin(actionable_features)]

    return jsonify({
        "actionable": df_actionable.to_dict(orient="records"),
        "conceptual": df_conceptual.to_dict(orient="records")
    })
