import datetime
import re

from flask import current_app
import pycountry
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship
import sqlalchemy as sa

from libreproperty.db import db
from libreproperty.utils import count_weekend_nights

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
    checkout_time = sa.Column(sa.Time, nullable=False, default=datetime.time(hour=10))
    amenities = sa.Column(sa.JSON)
    user_id = sa.Column(sa.ForeignKey("user.id"))
    user = relationship("User", back_populates="listings")
    base_price = sa.Column(sa.Integer)
    weekend_price = sa.Column(sa.Integer)
    currency = sa.Column(sa.String, default="USD")
    monthly_price_factor = sa.Column(sa.Numeric(precision=3, scale=1), default=1)
    weekly_price_factor = sa.Column(sa.Numeric(precision=3, scale=1), default=1)
    # guests_included_in_regular_fee = sa.Column(sa.Integer)
    # extra_person_fee = sa.Column(sa.Integer)
    cleaning_fee = sa.Column(sa.Integer, default=0)
    security_deposit = sa.Column(sa.Integer)
    is_listed = sa.Column(sa.Boolean, default=False)
    deleted = sa.Column(sa.Boolean, default=False)

    website = relationship("Website", back_populates="listing", uselist=False)
    bookings = relationship("Booking", back_populates="listing")

    @property
    def address(self):
        return f"{self.street}, {self.city}, {self.state[-2:]} {self.postal_code}"

    @property
    def city_state(self):
        return f"{self.city}, {self.state[-2:]}"

    @property
    def state_verbose(self):
        return pycountry.subdivisions.get(code=self.state).name

    def cost_cents(self, nights, weekend_nights):
        if not self.weekend_price:
            weekend_nights = 0
            weekend_cost_cents = 0
        if self.weekend_price:
            weekend_cost_cents = weekend_nights * self.weekend_price * 100

        nightly_cost = (nights - weekend_nights) * self.base_price * 100
        cleaning_fee = self.cleaning_fee if self.cleaning_fee else 0
        monthly_price_factor = self.monthly_price_factor if self.monthly_price_factor else 1
        weekly_price_factor = self.weekly_price_factor if self.weekly_price_factor else 1
        total_cost_cents = (cleaning_fee * 100) + (nightly_cost + weekend_cost_cents)
        if nights >= 30:
            total_cost_cents = total_cost_cents * monthly_price_factor
        elif 7 <= nights < 30:
            total_cost_cents = total_cost_cents * weekly_price_factor
        return total_cost_cents


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


class Website(db.Model, BasicMixin):
    subdomain = sa.Column(sa.String, unique=True, index=True)
    logo_text = sa.Column(sa.String)
    address_visible = sa.Column(sa.Boolean, default=False)
    location_description = sa.Column(sa.Text)
    listing_id = sa.Column(sa.ForeignKey("listing.id"))
    listing = relationship("Listing", back_populates="website")

    @classmethod
    def count(cls, subdomain):
        return cls.query.filter_by(subdomain=subdomain).count()


class Booking(db.Model, BasicMixin):
    checkin = sa.Column(sa.Date)
    checkout = sa.Column(sa.Date)
    guests = sa.Column(sa.Integer)
    first_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    email = sa.Column(sa.String)
    phone = sa.Column(sa.String)
    comments = sa.Column(sa.Text)
    amount_cents = sa.Column(sa.Integer)
    listing_id = sa.Column(sa.ForeignKey("listing.id"))
    listing = relationship("Listing", back_populates="bookings")

    @property
    def amount(self):
        return self.amount_cents / 100.0

    @property
    def nights(self) -> int:
        return (self.checkout - self.checkin).days

    @property
    def weekend_nights(self) -> int:
        return count_weekend_nights(self.checkin, self.checkout)
