from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard_bp', __name__, template_folder='templates')


@dashboard_bp.route("/dashboard")
def index():
    return render_template("dashboard/index.html")
