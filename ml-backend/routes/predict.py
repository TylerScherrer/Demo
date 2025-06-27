from flask import request, jsonify
import pandas as pd
import sys

# Fix stdout encoding to avoid crash on surrogate characters
sys.stdout.reconfigure(encoding='utf-8')

def register_predict_route(app, context):
    df = context["df"]
    model = context["model"]
    model_features = context["model_features"]
    category_features = context["category_features"]

    @app.route("/api/predict", methods=["POST"])
    def predict():
        try:
            data = request.get_json()
            print("\U0001f6e0 Incoming prediction request data:", data)

            if not data or "store" not in data:
                return jsonify({"error": "Missing 'store' in request"}), 400

            store = int(data.get("store"))
            months = int(data.get("months", 4))

            store_df = df[df["Store Number"] == store].copy()
            if store_df.empty:
                return jsonify({"error": f"No data found for store {store}"}), 404

            timeline = []
            store_df["Date"] = pd.to_datetime(store_df["Date"])
            weekly_sales = store_df.groupby(pd.Grouper(key="Date", freq="MS"))["Total_Sales"].sum().reset_index()
            history_rows = weekly_sales.tail(6)

            for i, row in enumerate(history_rows.itertuples(), start=-6):
                timeline.append({
                    "week": i,
                    "type": "actual",
                    "value": round(float(row.Total_Sales)),
                    "month_start": row.Date.strftime("%Y-%m-%d"),
                    "label": row.Date.strftime("%B %Y")
                })

            latest_row = store_df.iloc[-1:].copy()
            latest_date = latest_row["Date"].values[0]
            latest_week_start = pd.to_datetime(latest_date).replace(day=1)

            last_total = sum(latest_row[cat].values[0] for cat in category_features)
            category_shares = {
                cat.replace('_Sales', ''): (latest_row[cat].values[0] / last_total) if last_total > 0 else 0
                for cat in category_features
            }

            for col in model_features:
                if col not in latest_row.columns:
                    latest_row[col] = 0

            lag_values = [latest_row[col].values[0] for col in ['Lag_1', 'Lag_2', 'Lag_3', 'Lag_12'] if col in latest_row.columns]
            while len(lag_values) < 4:
                lag_values.append(0)

            for i in range(1, months + 1):
                forecast_month_start = (latest_week_start + pd.DateOffset(months=i)).replace(day=1)
                temp = latest_row.copy()
                temp['Lag_1'] = lag_values[-1]
                temp['Lag_2'] = lag_values[-2]
                temp['Lag_3'] = lag_values[-3]
                temp['Lag_12'] = lag_values[-4]

                for col in model_features:
                    if col not in temp.columns:
                        temp[col] = 0
                temp = temp[model_features]

                y = model.predict(temp)[0]
                lag_values.append(y)

                category_breakdown = {
                    cat: round(share * y, 2)
                    for cat, share in category_shares.items()
                    if share * y > 10
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

            print("\Final forecast timeline response:")
            for row in timeline:
                if row["type"] == "forecast":
                    print(f"{row['label']} \u2794 ${row['value']:.2f}")
                    print("  Category Breakdown:", row.get("category_breakdown", " Missing"))

            return jsonify({"timeline": timeline})

        except Exception as e:
            print(f" Exception in /api/predict: {e}")
            return jsonify({"error": "Internal server error"}), 500
