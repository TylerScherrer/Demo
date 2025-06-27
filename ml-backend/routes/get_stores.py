from flask import jsonify

def register_get_stores_route(app, context):
    df = context["df"]

    @app.route("/api/stores", methods=["GET"])
    def get_stores():
        try:
            if df is None:
                print("❌ DataFrame is None")
                return jsonify({"error": "features.csv not loaded"}), 500

            required_columns = ["Store Number", "City", "County"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                return jsonify({"error": f"Missing columns: {missing_columns}"}), 500

            store_info = (
                df[["Store Number", "City", "County"]]
                .dropna()
                .drop_duplicates()
                .sort_values("Store Number")
                .to_dict(orient="records")
            )

            print(f"✅ Extracted {len(store_info)} unique store records.")
            return jsonify({"stores": store_info})

        except Exception as e:
            print(f"❌ Exception in /api/stores: {e}")
            return jsonify({"error": "Internal server error"}), 500
