import datetime
import io

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField, IntegerField, SelectField, TimeField, SelectMultipleField, DecimalField, HiddenField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, ValidationError, Regexp
from wtforms import widgets
from wtform_address import CountrySelectField, StateSelectField
from markupsafe import Markup
from PIL import Image

from .amenities import amenities
from libreproperty.models import Website


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


class ListingForm(FlaskForm):
    title = StringField(validators=[DataRequired(), Length(min=3, max=255)])
    description = TextAreaField(label="Description (Optional)")
    street = StringField(validators=[DataRequired(), Length(min=3, max=255)])
    city = StringField(validators=[DataRequired(), Length(min=3, max=255)])
    state = StateSelectField(validators=[DataRequired(), Length(min=3, max=255)])
    postal_code = StringField(validators=[DataRequired(), Length(min=3, max=255)])
    country = CountrySelectField(default='US', validators=[DataRequired(), Length(min=2, max=2)])


class ListingPricingForm(FlaskForm):
    base_price = IntegerField(validators=[Optional()])
    weekend_price = IntegerField(validators=[Optional()])
    currency = SelectField(default="USD", choices=(('USD', 'USD'), ('EUR', 'EUR')),
                           validators=[Optional()])
    monthly_price_factor = DecimalField(default=1, places=2, validators=[Optional()])
    weekly_price_factor = DecimalField(default=1, places=2, validators=[Optional()])
    guests_included_in_regular_fee = IntegerField(validators=[Optional()])
    extra_person_fee = IntegerField(validators=[Optional()])
    cleaning_fee = IntegerField(validators=[Optional()])
    security_deposit = IntegerField(validators=[Optional()])


class ListingPropertyDetailsForm(FlaskForm):
    accommodates = IntegerField(description="The amount of people that are allowed to stay in your property",
                                validators=[Optional()])
    bedrooms = IntegerField(validators=[Optional()])
    beds = IntegerField(validators=[Optional()])
    bathrooms = IntegerField(validators=[Optional()])
    minimum_age = IntegerField(validators=[Optional()])
    min_nights = IntegerField(validators=[Optional()])
    max_nights = IntegerField(validators=[Optional()])
    cancellation_policy = SelectField(
        choices=[('flexible', 'Flexible'), ('moderate', 'Moderate'), ('firm', 'Firm'),
                 ('strict', 'Strict')])
    check_in_time = TimeField('Check-in Time', default=datetime.time(hour=13))
    check_out_time = TimeField('Check-out Time', default=datetime.time(hour=10))
    amenities = SelectMultipleField(choices=amenities, widget=select_multi_checkbox)


class ListingPhotoForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])
    caption = StringField()

    def validate_photo(form, field):
        try:
            Image.open(io.BytesIO(field.data.read())).verify()
            field.data.seek(0)
        except Exception as e:
            print(e)
            raise ValidationError('Photo must be a valid image')


class HiddenIntegerField(IntegerField):
    widget = widgets.HiddenInput()


class ListingPhotoDeleteForm(FlaskForm):
    photo_id = HiddenIntegerField(validators=[DataRequired()])


class ListingDeleteForm(FlaskForm):
    id = HiddenIntegerField(validators=[DataRequired()])


def unique_subdomain(form, field):
    if form.original_subdomain.data != field.data and Website.count(field.data) > 0:
        raise ValidationError(f"Subdomain {field.data} is already taken. Please choose another subdomain")


class WebsiteForm(FlaskForm):
    subdomain = StringField(validators=[
        DataRequired(), Length(min=3, max=255), unique_subdomain,
        Regexp(r"^[a-z\d]+$", message="Only lower case letters and numbers are allowed")
    ])
    logo_text = StringField(validators=[Length(max=15)])
    address_visible = BooleanField("Show exact address", render_kw={"class": "form-check-input mt-2"})
    location_description = TextAreaField("Location page: Description")

    original_subdomain = HiddenField()
