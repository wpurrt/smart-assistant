from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db


profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/")
@login_required
def profile():
    if not current_user.alice_link_code:
        current_user.generate_alice_code()
        db.session.commit()

    return render_template("profile.html", user=current_user)