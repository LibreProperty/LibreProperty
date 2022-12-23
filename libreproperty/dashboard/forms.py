import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, TimeField, SelectMultipleField, DecimalRangeField, BooleanField
from wtforms.validators import DataRequired, Length

from .amenities import amenities


class ListingForm(FlaskForm):
    title = StringField(validators=[DataRequired(), Length(min=3, max=255)])
    description = TextAreaField()
    accommodates = IntegerField()
    bedrooms = IntegerField()
    beds = IntegerField()
    bathrooms = IntegerField()
    minimum_age = IntegerField()
    min_nights = IntegerField()
    max_nights = IntegerField()
    cancellation_policy = SelectField(
        choices=[('flexible', 'Flexible'), ('moderate', 'Moderate'), ('firm', 'Firm'),
                 ('strict', 'Strict'), ('strict-long-term', 'Strict Long Term'),
                 ('flexible-long-term', 'Flexible Long Term'), ('non-refundable', 'Non-refundable')])
    check_in_time = TimeField('Check-in Time', default=datetime.time(hour=13))
    check_out_time = TimeField('Check-out Time', default=datetime.time(hour=10))
    amenities = SelectMultipleField(choices=amenities)
    base_price = IntegerField()
    weekend_price = IntegerField()
    currency = SelectField(default="USD", choices=(('USD', 'USD'), ('EUR', 'EUR')))
    monthly_price_factor = DecimalRangeField(default=1, places=2)
    weekly_price_factor = DecimalRangeField(default=1, places=2)
    guests_included_in_regular_fee = IntegerField()
    extra_person_fee = IntegerField()
    cleaning_fee = IntegerField()
    security_deposit = IntegerField()
    is_listed = BooleanField()

