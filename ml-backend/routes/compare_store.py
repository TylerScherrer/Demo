from flask import request, jsonify
import os
import requests
from flask_cors import cross_origin

def register_compare_route(app, context):
    print("📦 register_compare_route() is executing...")

    df = context.get("df")
    if df is None:
        raise ValueError("❌ DataFrame not found in context!")

    @app.route("/api/compare_store", methods=["POST", "OPTIONS"])
    @cross_origin()
    def compare_store():
        if request.method == "OPTIONS":
            return '', 204  # Preflight support

        try:
            data = request.get_json()
            print("📥 Incoming /compare_store data:", data)

            store_number = data.get("store")
            forecast_avg = data.get("forecast_avg")

            if not store_number or forecast_avg is None:
                msg = f"⚠️ Missing required inputs: store={store_number}, forecast_avg={forecast_avg}"
                print(msg)
                return jsonify({"error": msg}), 400

            # Calculate regional average sales
            all_stores_avg = df.groupby("Store Number")["Total_Sales"].sum().mean()
            print(f"🧮 Store #{store_number} vs Region Avg: {forecast_avg} vs {all_stores_avg:.2f}")

            # Create natural language prompt
            prompt = f"""
Compare this store's forecasted average monthly liquor sales to the average across all stores.

Store ID: {store_number}
Forecasted Monthly Average: ${forecast_avg:,.2f}
Region-Wide Monthly Average: ${all_stores_avg:,.2f}

Explain how this store is performing relative to others.
""".strip()

            # Prepare AI request
            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful retail analyst who compares store performance in plain language."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.6,
                "max_tokens": 200
            }

            headers = {
                "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            }

            print("🚀 Sending prompt to Groq AI API...")
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            print(f"🔁 Groq response status: {response.status_code}")

            if response.status_code != 200:
                print("❌ Error from Groq API:", response.text)
                return jsonify({"error": response.text}), 500

            ai_output = response.json()["choices"][0]["message"]["content"]
            print("✅ Groq AI Summary:", ai_output.strip())

            return jsonify({"summary": ai_output.strip()})

        except Exception as e:
            print("🔥 Exception in /api/compare_store:", str(e))
            return jsonify({"error": str(e)}), 500
