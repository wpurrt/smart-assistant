from flask import render_template
from app.main import main_bp
from flask_login import current_user, login_required
from app.models import ActionLog
from app.services.analytics_service import get_dashboard_stats


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    stats = get_dashboard_stats(current_user)
    recent_logs = ActionLog.query.filter_by(user_id=current_user.id).order_by(ActionLog.created_at.desc()).limit(5).all()
    return render_template("main/dashboard.html", stats=stats, recent_logs=recent_logs)