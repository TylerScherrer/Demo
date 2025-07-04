from flask import request, jsonify
import requests
import os
2
def register_explain_route(app, context):
    @app.route("/api/explain_forecast", methods=["POST"])
    def explain_forecast():
        try:
            data = request.get_json()
            timeline = data.get("timeline")
            print("🧪 Raw /api/explain_forecast input:", timeline)

            if not timeline:
                print("⚠️ Timeline is missing or empty.")
                return jsonify({"error": "No forecast provided"}), 400

            forecast_part = [f for f in timeline if f["type"] == "forecast"]
            if not forecast_part:
                print("⚠️ No forecast entries found in timeline.")
                return jsonify({"summary": "No forecast data available for explanation."})

            forecast_lines = "\n".join([f"{f['label']}: ${f['value']}" for f in forecast_part])
            user_prompt = (
                "Provide a simple, concise explanation of the following liquor sales forecast "
                "for a store manager with no data background:\n\n" + forecast_lines
            )

            print("📤 Prompt to Groq:\n", user_prompt)

            payload = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful retail analyst who explains forecast data clearly."
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 300
            }

            headers = {
                "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                print("❌ Groq API error:", response.text)
                return jsonify({"error": "Groq model request failed"}), 500

            explanation = response.json()["choices"][0]["message"]["content"]
            print("📬 AI Explanation output:", explanation)

            return jsonify({"summary": explanation.strip()})

        except Exception as e:
            print(f"❌ Forecast explanation error: {e}")
            return jsonify({"error": "Failed to generate explanation"}), 500
