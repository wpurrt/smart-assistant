from flask import render_template
from flask_login import login_required, current_user

from app.analytics import analytics_bp
from app.services.analytics_service import get_analytics_data
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services.analytics_service import get_user_analytics

@analytics_bp.route("/")
@login_required
def analytics_page():
    analytics = get_analytics_data(current_user)
    return render_template("analytics/index.html", analytics=analytics)


analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@login_required
def dashboard():
    stats = get_user_analytics(current_user)
    return render_template('analytics/dashboard.html', stats=stats)

@analytics_bp.route('/productivity')
@login_required
def productivity():
    stats = get_user_analytics(current_user)
    return render_template('analytics/productivity.html', stats=stats)