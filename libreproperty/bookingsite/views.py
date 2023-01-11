from flask import Blueprint, render_template

from libreproperty.models import Website, db

bookingsite_bp = Blueprint('bookingsite_bp', __name__, template_folder='templates')


@bookingsite_bp.route("/<site_id>")
def index(site_id):
    site_id = int(site_id)
    site = db.session.execute(
        db.select(Website).filter(Website.id == site_id)
    ).scalar()
    return render_template("bookingsite/index.html", site=site, title="Book today!")
