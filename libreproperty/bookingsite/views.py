from flask import Blueprint, render_template, abort, request

from libreproperty.models import Website, db
from .forms import BookingForm

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
    form = BookingForm()
    if form.validate_on_submit():
        print("Create a booking")
    site = get_site_or_404(subdomain)
    checkin = request.args.get("checkin")
    checkout = request.args.get("checkout")
    guests = int(request.args.get("guests", 1))
    return render_template("bookingsite/booking.html", site=site, checkin=checkin, checkout=checkout, guests=guests,
                           form=form)
