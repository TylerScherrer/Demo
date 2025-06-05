# routes/ai_summary.py
import os
import logging
from flask import Blueprint, request, jsonify
import openai
from dotenv import load_dotenv

# Load environment variables first
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

ai_summary_bp = Blueprint("ai_summary", __name__)

# Read API key
oai_key = os.getenv("OPENAI_API_KEY")
if not oai_key:
    logging.error("OPENAI_API_KEY is not set!")
else:
    openai.api_key = oai_key

@ai_summary_bp.route("", methods=["POST"], strict_slashes=False)
def generate_forecast_summary():
    """
    POST /ai-summary
    Expects JSON: {"forecastSummary": {...}}
    Returns: {"summary": "..."}
    """
    logging.debug("[ai_summary] endpoint hit")
    data = request.get_json(silent=True) or {}
    logging.debug("[ai_summary] payload: %s", data)

    forecast = data.get("forecastSummary")
    if not forecast:
        return jsonify({"error": "missing forecastSummary"}), 400

    prompt = (
        f"Summarize this sales forecast for presentation:\n"
        f"- Total sales: ${forecast['totalPredicted']} over {forecast['weeks']} weeks.\n"
        f"- 95% confidence range: ${forecast['confidence_low']} – ${forecast['confidence_high']}."
    )
    logging.debug("[ai_summary] prompt: %s", prompt)

    try:
        # Updated for openai>=1.0.0
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150,
        )
        logging.debug("[ai_summary] raw resp: %s", resp)
        summary = resp.choices[0].message.content.strip()
        return jsonify({"summary": summary})
    except Exception as ex:
        logging.exception("AI summary error")
        return jsonify({"error": "OpenAI API error"}), 500