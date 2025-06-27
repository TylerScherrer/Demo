from flask import request, jsonify
import torch

def register_explain_route(app, context):

    phi_model = context["phi_model"]
    tokenizer = context["tokenizer"]

    @app.route("/api/explain_forecast", methods=["POST"])
    def explain_forecast():
        if not phi_model or not tokenizer:
            return jsonify({"error": "Phi-1.5 model not available"}), 500

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

            prompt = (
                "Provide a concise and clear summary (without exercises or additional tasks) "
                "analyzing the following monthly liquor sales forecast for a store manager:\n\n"
                + "\n".join([f"{f['label']}: ${f['value']}" for f in forecast_part])
            )

            print("📤 Prompt to model:\n", prompt)

            inputs = tokenizer(prompt, return_tensors="pt", padding=True)
            input_ids = inputs["input_ids"]
            attention_mask = inputs["attention_mask"]

            if torch.isnan(input_ids).any() or torch.isinf(input_ids).any():
                print("❌ NaN or Inf detected in input_ids")
                return jsonify({"summary": "Input tensor invalid — NaN or Inf detected."})

            outputs = phi_model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=100,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=True,
                temperature=0.7,
                top_k=50,
                top_p=0.95
            )

            try:
                decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
                print("📜 Decoded response:", repr(decoded))

                if decoded.startswith(prompt):
                    explanation = decoded[len(prompt):].strip()
                else:
                    explanation = decoded.strip()

                if not explanation or explanation.lower().startswith("exercise") or "graph" in explanation.lower():
                    print("⚠️ Unusable explanation, fallback triggered.")
                    explanation = "Sales are forecasted to decline over the next few weeks. Please monitor trends."

            except Exception as decode_err:
                print(f"❌ Decoding failed: {decode_err}")
                explanation = "Model produced an unreadable result."

            print("📬 AI Explanation output:", explanation)

            return jsonify({"summary": explanation or "The forecast suggests a trend, but no summary was returned."})

        except Exception as e:
            print(f"❌ Phi-1.5 inference error: {e}")
            return jsonify({"error": "Failed to generate explanation"}), 500
