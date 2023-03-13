import logging
from random import choice
from string import ascii_lowercase

import botocore.exceptions
from flask import Blueprint, current_app, render_template, url_for, redirect, abort, request, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from libreproperty.models import Listing, Photo, Website
from libreproperty.s3 import get_s3_client
from libreproperty.tasks.tasks import store_airbnb_photos
from libreproperty import db
from libreproperty import airbnb

from .forms import (
    ListingForm, ListingPricingForm, ListingPropertyDetailsForm, ListingPhotoForm, ListingPhotoDeleteForm,
    ListingDeleteForm, WebsiteForm, ListingFromAirbnbForm
)

dashboard_bp = Blueprint('dashboard_bp', __name__, template_folder='templates')


@dashboard_bp.route("/")
@login_required
def index():
    listings = db.session.execute(
        db.select(Listing).filter(Listing.user_id == current_user.id).filter(Listing.deleted.isnot(True))
    ).scalars().all()
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
        return redirect(url_for('dashboard_bp.update_listing_pricing', listing_id=listing.id))
    return render_template("dashboard/create_listing.html", form=form)


@dashboard_bp.route("/create-listing-from-airbnb", methods=["GET", "POST"])
@login_required
def create_listing_from_airbnb():
    form = ListingFromAirbnbForm()
    if form.validate_on_submit():
        airbnb_listing_id = form.listing_id()
        airbnb_listing = airbnb.Listing.load(airbnb_listing_id)
        listing = airbnb_listing.create_lp_listing()
        listing.country = "US"
        listing.user_id = current_user.id
        listing.base_price = form.base_price.data
        db.session.add(listing)
        db.session.commit()
        result = store_airbnb_photos(listing_id=listing.id, photos=airbnb_listing.photos)
        logging.info(f"Created task to store airbnb photos for listing {listing.id}: {result}")
        flash('Import was successful. Please wait a minute or so while photos are imported.', 'success')
        return redirect(url_for('dashboard_bp.update_listing', listing_id=listing.id))
    return render_template("dashboard/create_listing_from_airbnb.html", form=form)


def get_secure_listing(listing_id) -> Listing:
    l_id = int(listing_id)
    listing = db.session.execute(db.select(Listing).filter(
        Listing.id == l_id)).scalar()
    if listing.user_id != current_user.id:
        return abort(403)
    return listing


def get_secure_photo(photo_id) -> Photo:
    p_id = int(photo_id)
    photo = db.session.execute(db.select(Photo).filter(
        Photo.id == p_id)).scalar()
    if photo.listing.user_id != current_user.id:
        return abort(403)
    return photo


def get_secure_website(website_id) -> Website:
    w_id = int(website_id)
    website = db.session.execute(db.select(Website).filter(
        Website.id == w_id)).scalar()
    if website.listing.user_id != current_user.id:
        return abort(403)
    return website


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
    form = ListingPhotoForm()
    if request.method == "GET":
        form.process(obj=listing)
    if form.validate_on_submit():
        s3 = get_s3_client()
        bucket = current_app.config.get("BUCKET")
        random_str = ''.join(choice(ascii_lowercase) for i in range(4))
        key = f'{str(listing.id)}-{random_str}-{secure_filename(form.photo.data.filename)}'
        s3.upload_fileobj(form.photo.data, bucket, key)
        location = f"s3://{bucket}/{key}"
        photo = Photo(location=location, caption=form.caption.data, listing_id=listing.id)
        db.session.add(photo)
        db.session.commit()
        flash(f'Property photo {key} was added successfully', 'success')
        return redirect(url_for('dashboard_bp.update_listing_photos', listing_id=listing_id))
    return render_template("dashboard/update_listing_photos.html", form=form, listing=listing, title="Add a photo")


@dashboard_bp.route("/update-listing/<listing_id>/delete-photo", methods=["POST"])
@login_required
def delete_listing_photo(listing_id):
    listing = get_secure_listing(listing_id)
    form = ListingPhotoDeleteForm()
    photo = get_secure_photo(form.photo_id.data)
    if form.validate_on_submit():
        try:
            s3 = get_s3_client()
            s3.delete_object(Bucket=photo.bucket, Key=photo.object_key)
        except botocore.exceptions.ClientError as err:
            logging.error("S3 client error while deleting object: %s", err)
        except Exception as err:
            logging.error("Unexpected error while deleting object: %s", err)

        db.session.delete(photo)
        db.session.commit()
        flash(f'Property photo {photo.object_key} was deleted successfully', 'success')
        return redirect(url_for('dashboard_bp.update_listing_photos', listing_id=listing_id))
    return render_template("dashboard/update_listing_photos.html", form=form, listing=listing, title="Add a photo")


@dashboard_bp.route("/delete-listing", methods=["POST"])
@login_required
def delete_listing():
    form = ListingDeleteForm()
    listing = get_secure_listing(form.id.data)
    if form.validate_on_submit():
        listing.deleted = True
        db.session.commit()
        flash(f'Listing {listing.id}: {listing.title} was deleted successfully', 'success')
        return redirect(url_for('dashboard_bp.index'))
    else:
        flash(f'Listing {listing.id}:{listing.title} was deleted successfully', 'success')
        return redirect(url_for('dashboard_bp.index'))


@dashboard_bp.route("/update-listing/<listing_id>/create-website", methods=["GET", "POST"])
@login_required
def create_website(listing_id):
    listing = get_secure_listing(listing_id)
    if listing.website:
        flash('You already had an existing website created. So redirected you to that one instead.', 'warning')
        return redirect(url_for('dashboard_bp.update_website', listing_id=listing_id, website_id=listing.website.id))
    form = WebsiteForm()
    if form.validate_on_submit():
        if not listing.state or not listing.street or not listing.city:
            flash("Please add your full address including state, street and city before creating a website.", "danger")
            return redirect(url_for('dashboard_bp.update_listing', listing_id=listing_id))
        website = Website()
        website.listing_id = listing.id
        form.populate_obj(website)
        db.session.add(website)
        db.session.commit()
        flash('Website was created successfully', 'success')
        return redirect(url_for('dashboard_bp.update_website', listing_id=listing_id, website_id=website.id))
    return render_template("dashboard/update_listing.html", form=form, listing=listing, title="Create Website")


@dashboard_bp.route("/update-listing/<listing_id>/update-website/<website_id>", methods=["GET", "POST"])
@login_required
def update_website(listing_id, website_id):
    listing = get_secure_listing(listing_id)
    website = get_secure_website(website_id)
    form = WebsiteForm()
    if request.method == "GET":
        form.process(obj=website)
        form.original_subdomain.data = website.subdomain
    if form.validate_on_submit():
        form.populate_obj(website)
        db.session.commit()
        flash('Website was updated successfully', 'success')
        return redirect(url_for('dashboard_bp.update_website', listing_id=listing_id, website_id=website.id))
    return render_template("dashboard/update_listing.html", form=form, listing=listing, title="Update Website")
