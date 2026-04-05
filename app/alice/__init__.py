from flask import Blueprint


alice_bp = Blueprint("alice", __name__)


from app.alice import routes