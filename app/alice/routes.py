from flask import Blueprint, request, jsonify
from app.services.alice_service import handle_alice_command


alice_bp = Blueprint("alice", __name__)


@alice_bp.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    response_text = handle_alice_command(data)
    return jsonify({
        "response": {
            "text": response_text,
            "end_session": False
        }
    })