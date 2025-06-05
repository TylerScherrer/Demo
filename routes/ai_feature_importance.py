import os
import logging
import openai
from flask import Blueprint, request, jsonify

# Load environment variables early
from dotenv import load_dotenv
load_dotenv()  # ← ensure OPENAI_API_KEY is in os.environ before we set it

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Blueprint
ai_feature_importance_bp = Blueprint("ai_feature_importance", __name__)

# Read API key from env
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logging.error("OPENAI_API_KEY is not set!")

@ai_feature_importance_bp.route("", methods=["POST"], strict_slashes=False)
def ai_feature_importance():
    """
    Expects JSON:
    {
      "actionable": [ {"feature": "...", "importance": ...}, ... ],
      "conceptual": [ {"feature": "...", "importance": ...}, ... ]
    }
    Returns:
      { "summary": "<plain-English summary>" }
    """
    data = request.get_json() or {}
    actionable = data.get("actionable", [])
    conceptual = data.get("conceptual", [])
    if not actionable and not conceptual:
        return jsonify({"error": "Missing actionable and/or conceptual data"}), 400

    # Helper: format top‑3 features
    def fmt_feats(lst):
        top = sorted(lst, key=lambda x: x.get("importance", 0), reverse=True)[:3]
        return ", ".join(f"{f['feature']} ({f['importance']*100:.1f}%)" for f in top) or "None"

    actionable_str = fmt_feats(actionable)
    conceptual_str = fmt_feats(conceptual)

    prompt = (
        f"You are a data assistant. Below are top feature importances from an ML model predicting liquor sales:\n"
        f"- Actionable features: {actionable_str}\n"
        f"- Conceptual (context) features: {conceptual_str}\n\n"
        "Provide a brief plain-English summary explaining how these influence predictions "
        "and suggest any actions a store manager could take."
    )

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        summary = resp.choices[0].message.content.strip()
        return jsonify({"summary": summary})
    except Exception as e:
        logging.exception("OpenAI API error in ai_feature_importance")
        return jsonify({"error": "OpenAI API error"}), 500
