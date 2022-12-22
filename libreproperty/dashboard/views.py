from flask import Blueprint, render_template
from flask_login import login_required, current_user

from libreproperty.models import Listing
from libreproperty import db

dashboard_bp = Blueprint('dashboard_bp', __name__, template_folder='templates')


@login_required
@dashboard_bp.route("/")
def index():
    listings = db.session.execute(db.select(Listing).filter(Listing.user_id == current_user.id)).scalars().all()
    return render_template("dashboard/index.html", listings=listings)


@dashboard_bp.route("/create-listing")
def create_listing():
    return "hi"
