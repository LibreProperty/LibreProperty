from flask import Blueprint, render_template, abort

from libreproperty.models import Website, db

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
