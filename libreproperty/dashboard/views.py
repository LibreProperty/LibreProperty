from flask import Blueprint, render_template, url_for, redirect, abort, request, flash
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


@dashboard_bp.route("/create-listing", methods=["GET", "POST"])
@login_required
def create_listing():
    form = ListingForm()
    if form.validate_on_submit():
        listing = Listing()
        listing.user_id = current_user.id
        form.populate_obj(listing)
        db.session.add(listing)
        db.session.commit()
        return redirect(url_for('dashboard_bp.index'))
    return render_template("dashboard/create_listing.html", form=form)


@dashboard_bp.route("/update-listing/<listing_id>", methods=["GET", "POST"])
@login_required
def update_listing(listing_id):
    listing_id = int(listing_id)
    listing = db.session.execute(db.select(Listing).filter(
        Listing.id == listing_id)).scalar()
    if listing.user_id != current_user.id:
        return abort(403)
    form = ListingForm()
    if request.method == "GET":
        form.process(obj=listing)
    if form.validate_on_submit():
        listing.user_id = current_user.id
        form.populate_obj(listing)
        db.session.commit()
        flash('Update was successful', 'success')
        return redirect(url_for('dashboard_bp.update_listing', listing_id=listing_id))
    return render_template("dashboard/update_listing.html", form=form)
