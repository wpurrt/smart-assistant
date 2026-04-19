from flask import render_template
from flask_login import login_required, current_user
from app.analytics import analytics_bp
from app.services.analytics_service import get_dashboard_stats


@analytics_bp.route("/")
@login_required
def analytics():
    stats = get_dashboard_stats(current_user)
    return render_template("analytics/dashboard.html", stats=stats)
