from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from flask import Blueprint, render_template, flash, redirect, url_for

from app.services.alice_service import ensure_alice_code
from app.extensions import db
from app.forms import GenerateAliceCodeForm
from app.models import UserAliceLink
from app.profile import profile_bp
from app.services.alice_service import generate_link_code


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def profile_page():
    form = GenerateAliceCodeForm()
    if form.validate_on_submit():
        link = current_user.alice_link
        if link and link.is_linked:
            flash("Аккаунт уже привязан к Яндекс Алисе.", "info")
            return redirect(url_for("profile.profile_page"))
        if not link:
            code = generate_link_code()
            while UserAliceLink.query.filter_by(link_code=code).first():
                code = generate_link_code()
            link = UserAliceLink(
                user_id=current_user.id,
                link_code=code
            )
            db.session.add(link)
        else:
            code = generate_link_code()
            while UserAliceLink.query.filter_by(link_code=code).first():
                code = generate_link_code()
            link.link_code = code
        db.session.commit()
        flash("Новый код привязки сгенерирован.", "success")
        return redirect(url_for("profile.profile_page"))

    return render_template("profile/index.html", form=form)


profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/')
@login_required
def profile():
    form = GenerateAliceCodeForm()
    return render_template('profile/profile.html', form=form)

@profile_bp.route('/generate-alice-code', methods=['POST'])
@login_required
def generate_alice_code():
    form = GenerateAliceCodeForm()

    if form.validate_on_submit():
        ensure_alice_code(current_user)
        flash('Код привязки Алисы обновлён.', 'success')

    return redirect(url_for('profile.profile'))