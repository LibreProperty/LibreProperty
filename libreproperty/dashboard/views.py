from flask import Blueprint, render_template, url_for, redirect
from flask_login import login_required, current_user

from libreproperty.models import Listing
from libreproperty import db

from .forms import ListingForm

dashboard_bp = Blueprint('dashboard_bp', __name__, template_folder='templates')


@dashboard_bp.route("/")
@login_required
def index():
    listings = db.session.execute(db.select(Listing).filter(Listing.user_id == current_user.id)).scalars().all()
    return render_template("dashboard/index.html", listings=listings)


@dashboard_bp.route("/create-listing")
@login_required
def create_listing():
    form = ListingForm()
    return render_template("dashboard/create_listing.html", form=form)
