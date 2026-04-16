from flask import render_template
from flask_login import login_required, current_user

from app.analytics import analytics_bp
from app.services.analytics_service import get_analytics_data


@analytics_bp.route("/")
@login_required
def analytics_page():
    analytics = get_analytics_data(current_user)
    return render_template("analytics/index.html", analytics=analytics)