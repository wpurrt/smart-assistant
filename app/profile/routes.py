from flask import render_template
from flask_login import login_required, current_user
from app.profile.forms import GenerateAliceCodeForm
from app.profile import profile_bp
from app.extensions import db


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def profile():
    form = GenerateAliceCodeForm()

    #нажали кнопку генерации кода
    if form.validate_on_submit():
        current_user.generate_alice_code()
        db.session.commit()

    return render_template("profile/index.html", user=current_user, form=form)