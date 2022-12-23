from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

pages_bp = Blueprint('pages_bp', __name__, template_folder='templates')


@pages_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_bp.index'))
    return render_template("index.html")
