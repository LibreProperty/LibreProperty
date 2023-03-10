import datetime

from flask import Blueprint, render_template, abort, request, redirect, url_for, flash

from libreproperty.models import Website, Booking, Message, db
from .forms import BookingForm, ContactForm

bookingsite_bp = Blueprint('bookingsite_bp', __name__, template_folder='templates')


def get_site_or_404(subdomain):
    site = db.session.execute(db.select(Website).filter(Website.subdomain == subdomain)).scalar()
    if not site:
        return abort(404)
    return site


@bookingsite_bp.route("/", subdomain="<subdomain>")
def subdomain_index(subdomain):
    site = get_site_or_404(subdomain)
    return render_template("bookingsite/index.html", site=site, title="Book today!")


@bookingsite_bp.route("/location", subdomain="<subdomain>")
def location(subdomain):
    site = get_site_or_404(subdomain)
    return render_template("bookingsite/location.html", site=site, title="")


@bookingsite_bp.route("/pricing", subdomain="<subdomain>")
def pricing(subdomain):
    site = get_site_or_404(subdomain)
    return render_template("bookingsite/pricing.html", site=site, title="")


@bookingsite_bp.route("/booking", subdomain="<subdomain>", methods=["GET", "POST"])
def booking(subdomain):
    site = get_site_or_404(subdomain)
    form = BookingForm()
    if form.validate_on_submit():
        booking_db = Booking()
        form.populate_obj(booking_db)
        booking_db.listing_id = site.listing.id
        booking_db.amount_cents = site.listing.cost_cents(booking_db.nights, booking_db.weekend_nights)
        db.session.add(booking_db)
        db.session.commit()
        flash("Your request to book was submitted. Please wait for the host to respond before making any plans.", "success")
        return redirect(url_for('bookingsite_bp.booking', subdomain=site.subdomain))
    checkin = request.args.get("checkin")
    checkout = request.args.get("checkout")
    guests = int(request.args.get("guests", 1))
    form.checkin.data = datetime.datetime.strptime(checkin, "%m/%d/%Y") if checkin else None
    form.checkout.data = datetime.datetime.strptime(checkout, "%m/%d/%Y") if checkout else None
    form.guests.data = guests
    return render_template("bookingsite/booking.html", site=site, form=form)


@bookingsite_bp.route("/contact", subdomain="<subdomain>", methods=["GET", "POST"])
def contact(subdomain):
    site = get_site_or_404(subdomain)
    form = ContactForm()
    if form.validate_on_submit():
        message_db = Message()
        form.populate_obj(message_db)
        message_db.listing_id = site.listing.id
        db.session.add(message_db)
        db.session.commit()
        flash("Your message has been submitted. The host will get back to you as soon as possible.", "success")
        return redirect(url_for('bookingsite_bp.contact', subdomain=site.subdomain))
    return render_template("bookingsite/contact.html", site=site, form=form)
