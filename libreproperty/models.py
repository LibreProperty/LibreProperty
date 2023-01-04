import datetime
import re

from flask import current_app
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship
import sqlalchemy as sa

from libreproperty.db import db

Base = declarative_base()


class BasicMixin(object):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_on = db.Column(db.DateTime, index=False, unique=False, server_default=func.now())
    updated_on = db.Column(db.DateTime, onupdate=func.now())


class Listing(db.Model, BasicMixin):
    title = sa.Column(sa.String, nullable=False)
    street = sa.Column(sa.String)
    city = sa.Column(sa.String)
    state = sa.Column(sa.String)
    postal_code = sa.Column(sa.String)
    country = sa.Column(sa.String)
    description = sa.Column(sa.Text)
    source = sa.Column(sa.String)
    source_id = sa.Column(sa.String)
    accommodates = sa.Column(sa.Integer)
    bedrooms = sa.Column(sa.Integer)
    beds = sa.Column(sa.Integer)
    bathrooms = sa.Column(sa.Integer)
    minimum_age = sa.Column(sa.Integer)
    photos = relationship("Photo", back_populates="listing")
    min_nights = sa.Column(sa.Integer)
    max_nights = sa.Column(sa.Integer)
    cancellation_policy = sa.Column(sa.String)
    check_in_time = sa.Column(sa.Time, nullable=False, default=datetime.time(hour=15))
    checkout_in_time = sa.Column(sa.Time, nullable=False, default=datetime.time(hour=10))
    amenities = sa.Column(sa.JSON)
    user_id = sa.Column(sa.ForeignKey("user.id"))
    user = relationship("User", back_populates="listings")
    base_price = sa.Column(sa.Integer)
    weekend_price = sa.Column(sa.Integer)
    currency = sa.Column(sa.String, default="USD")
    monthly_price_factor = sa.Column(sa.Numeric(precision=3, scale=1), default=1)
    weekly_price_factor = sa.Column(sa.Numeric(precision=3, scale=1), default=1)
    guests_included_in_regular_fee = sa.Column(sa.Integer)
    extra_person_fee = sa.Column(sa.Integer)
    cleaning_fee = sa.Column(sa.Integer)
    security_deposit = sa.Column(sa.Integer)
    is_listed = sa.Column(sa.Boolean, default=False)
    deleted = sa.Column(sa.Boolean, default=False)


class Photo(db.Model, BasicMixin):
    location = sa.Column(sa.String, nullable=False)
    thumbnail_location = sa.Column(sa.String)
    caption = sa.Column(sa.String)
    listing_id = sa.Column(sa.ForeignKey("listing.id"))
    listing = relationship("Listing", back_populates="photos")

    @property
    def bucket(self):
        return re.search(r"s3://([a-zA-Z1-9.-]+)/*", self.location).groups()[0]

    @property
    def object_key(self):
        return re.search(r"s3://[a-zA-Z1-9.-]+/(.*)$", self.location).groups()[0]

    @property
    def url(self):
        if current_app.config.get("S3_ENDPOINT").lower() == "aws":
            # TODO: check if regional buckets are needed/supported
            return f'https://{self.bucket}.s3.amazonaws.com/{self.object_key}'
        else:
            base = current_app.config.get("S3_ENDPOINT")
            return f'{base}/{self.bucket}/{self.object_key}'
