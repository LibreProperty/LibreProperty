import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, TimeField, SelectMultipleField, DecimalRangeField, BooleanField
from wtforms.validators import DataRequired, Length
from wtforms import widgets
from markupsafe import Markup
from wtforms import SelectField
import pycountry

from .amenities import amenities


def select_multi_checkbox(field, **kwargs):
    kwargs.setdefault('type', 'checkbox')
    field_id = kwargs.pop('id', field.id)
    html = [u'<div %s>' % widgets.html_params(id=field_id, class_="select-multi-checkbox")]
    for value, label, checked in field.iter_choices():
        choice_id = u'%s-%s' % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        html.append(u'<div class="form-check form-check-inline">')
        if checked:
            options['checked'] = 'checked'
        html.append(u'<input class="field-check-input" %s />' % widgets.html_params(**options))
        html.append(u'<label class="form-check-label px-2" for="%s">%s</label></li>' % (field_id, label))
        html.append(u'</div>')
    html.append(u'</div>')
    return Markup(u''.join(html))


class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [(country.alpha_2, country.name) for country in pycountry.countries]


def get_states(country_code: str):
    states = [(state.code, state.name) for state in pycountry.subdivisions.get(country_code=country_code)]
    states.sort(key=lambda x: x[1])
    return states


class StateSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        country = kwargs.get("country", "US")
        super(StateSelectField, self).__init__(*args, **kwargs)
        self.choices = get_states("US")


class ListingForm(FlaskForm):
    title = StringField(description="Title of property", validators=[DataRequired(), Length(min=3, max=255)])
    street = StringField()
    city = StringField()
    state = StateSelectField()
    postal_code = StringField()
    country = CountrySelectField(default='US')
    address = StringField()
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
    amenities = SelectMultipleField(choices=amenities, widget=select_multi_checkbox)

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

