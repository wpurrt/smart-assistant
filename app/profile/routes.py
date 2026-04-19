from flask import render_template, flash, redirect, url_for
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


@profile_bp.route("/generate_code", methods=["POST"])
@login_required
def generate_code():
    current_user.generate_alice_code()
    db.session.commit()
    flash("Код сгенерирован", "success")
    return redirect(url_for("profile.profile"))