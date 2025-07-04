from flask import jsonify
import pandas as pd  # ✅ Ensure this is imported

def register_get_stores_route(app, context):
    df = context["df"]

    @app.route("/api/stores", methods=["GET"])
    def get_stores():
        try:
            if df is None:
                print("❌ DataFrame is None")
                return jsonify({"error": "features.csv not loaded"}), 500

            required_columns = ["Store Number", "City", "County", "Date"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                return jsonify({"error": f"Missing columns: {missing_columns}"}), 500

            # ✅ Ensure Date is datetime
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

            # ✅ Filter to only include stores with data from 2020+
            recent_data = df[df["Date"].dt.year >= 2020]

            store_info = (
                recent_data[["Store Number", "City", "County"]]
                .dropna()
                .drop_duplicates()
                .sort_values("Store Number")
                .to_dict(orient="records")
            )

            print(f"✅ Extracted {len(store_info)} unique store records (2020+).")
            return jsonify({"stores": store_info})

        except Exception as e:
            print(f"❌ Exception in /api/stores: {e}")
            return jsonify({"error": "Internal server error"}), 500
