from flask import Blueprint, render_template

pages_bp = Blueprint('pages_bp', __name__, template_folder='templates')


@pages_bp.route("/")
def index():
    return render_template("index.html")