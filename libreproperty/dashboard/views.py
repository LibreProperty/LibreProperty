from random import choice
from string import ascii_lowercase

import boto3
from flask import Blueprint, current_app, render_template, url_for, redirect, abort, request, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from libreproperty.models import Listing, Photo
from libreproperty import db

from .forms import ListingForm, ListingPricingForm, ListingPropertyDetailsForm, ListingPhotosForm

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


def get_secure_listing(listing_id):
    l_id = int(listing_id)
    listing = db.session.execute(db.select(Listing).filter(
        Listing.id == l_id)).scalar()
    if listing.user_id != current_user.id:
        return abort(403)
    return listing


@dashboard_bp.route("/update-listing/<listing_id>", methods=["GET", "POST"])
@login_required
def update_listing(listing_id):
    listing = get_secure_listing(listing_id)
    form = ListingForm()
    if request.method == "GET":
        form.process(obj=listing)
    if form.validate_on_submit():
        form.populate_obj(listing)
        db.session.commit()
        flash('Update was successful', 'success')
        return redirect(url_for('dashboard_bp.update_listing', listing_id=listing_id))
    return render_template("dashboard/update_listing.html", form=form, listing=listing, title="Update Basic Info")


@dashboard_bp.route("/update-listing/<listing_id>/pricing", methods=["GET", "POST"])
@login_required
def update_listing_pricing(listing_id):
    listing = get_secure_listing(listing_id)
    form = ListingPricingForm()
    if request.method == "GET":
        form.process(obj=listing)
    if form.validate_on_submit():
        form.populate_obj(listing)
        db.session.commit()
        flash('Pricing update was successful', 'success')
        return redirect(url_for('dashboard_bp.update_listing', listing_id=listing_id))
    return render_template("dashboard/update_listing.html", form=form, listing=listing, title="Update Pricing")


@dashboard_bp.route("/update-listing/<listing_id>/property-details", methods=["GET", "POST"])
@login_required
def update_listing_property_details(listing_id):
    listing = get_secure_listing(listing_id)
    form = ListingPropertyDetailsForm()
    if request.method == "GET":
        form.process(obj=listing)
    if form.validate_on_submit():
        form.populate_obj(listing)
        db.session.commit()
        flash('Property details update was successful', 'success')
        return redirect(url_for('dashboard_bp.update_listing_property_details', listing_id=listing_id))
    return render_template("dashboard/update_listing.html", form=form, listing=listing, title="Update Property Details")


@dashboard_bp.route("/update-listing/<listing_id>/photos", methods=["GET", "POST"])
@login_required
def update_listing_photos(listing_id):
    listing = get_secure_listing(listing_id)
    form = ListingPhotosForm()
    if request.method == "GET":
        form.process(obj=listing)
    if form.validate_on_submit():
        s3 = boto3.client(
            "s3",
            endpoint_url=current_app.config.get("S3_ENDPOINT"),
            config=boto3.session.Config(signature_version='s3v4'),
            aws_session_token=None,
            verify=current_app.config.get("S3_VERIFY")
        )
        bucket = current_app.config.get("BUCKET")
        random_str = ''.join(choice(ascii_lowercase) for i in range(4))
        key = f'{str(listing.id)}-{random_str}-{secure_filename(form.photo.data.filename)}'
        s3.upload_fileobj(form.photo.data.stream, bucket, key)
        location = "s3://{bucket}/{key}"
        photo = Photo(location=location, caption=form.caption.data, listing_id=listing.id)
        db.session.add(photo)
        db.session.commit()
        flash(f'Property photo {key} was added successfully', 'success')
        return redirect(url_for('dashboard_bp.update_listing_photos', listing_id=listing_id))
    return render_template("dashboard/update_listing.html", form=form, listing=listing, title="Add a photo")
