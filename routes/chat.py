# routes/chat.py
import os
import logging
from flask import Blueprint, request, jsonify
import openai
from dotenv import load_dotenv

# Load env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

logging.basicConfig(level=logging.DEBUG)
chat_bp = Blueprint("chat", __name__)

oai_key = os.getenv("OPENAI_API_KEY")
if not oai_key:
    logging.error("OPENAI_API_KEY is not set!")
else:
    openai.api_key = oai_key

@chat_bp.route("/chat", methods=["POST"], strict_slashes=False)
def chat():
    """
    POST /api/chat
    JSON: {"question": str, "chartType": str, "chartData": list}
    Returns: {"reply": str}
    """
    logging.debug("[chat] endpoint hit")
    payload = request.get_json(silent=True) or {}
    logging.debug("[chat] payload: %s", payload)

    question = payload.get("question")
    chart_type = payload.get("chartType")
    chart_data = payload.get("chartData")
    if not question or not chart_data:
        return jsonify({"error": "Missing question or chartData"}), 400

    # Build a simple system + user prompt
    messages = [
        {"role": "system", "content": "You are an assistant for data charts."},
        {"role": "user", "content": f"{question} Data: {chart_data}"}
    ]
    try:
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        logging.debug("[chat] raw resp: %s", resp)
        reply = resp.choices[0].message.content.strip()
        return jsonify({"reply": reply})
    except Exception as ex:
        logging.exception("OpenAI chat error")
        return jsonify({"error": "OpenAI API error"}), 500
