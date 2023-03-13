from flask_wtf import FlaskForm

from wtforms import DateField, IntegerField, StringField, EmailField, TextAreaField
from wtforms.validators import DataRequired


class BookingForm(FlaskForm):
    checkin = DateField(format="%m/%d/%Y", validators=[DataRequired("Please tell us when you're checking in")])
    checkout = DateField(format="%m/%d/%Y", validators=[DataRequired("Please tell us when you're checking out")])
    guests = IntegerField(validators=[DataRequired()])
    first_name = StringField(validators=[DataRequired("Please provide your first name")])
    last_name = StringField(validators=[DataRequired("Please provide your last name")])
    email = EmailField(validators=[DataRequired("Please provide a valid email address")])
    phone = StringField(validators=[DataRequired("Please provide a phone number")])
    comments = TextAreaField(validators=[DataRequired("Please provide a short introduction and reason for your stay")])


class ContactForm(FlaskForm):
    first_name = StringField(validators=[DataRequired("Please provide your first name")])
    last_name = StringField(validators=[DataRequired("Please provide your last name")])
    email = EmailField(validators=[DataRequired("Please provide a valid email address")])
    phone = StringField(validators=[DataRequired("Please provide a phone number")])
    comments = TextAreaField(validators=[DataRequired("Please provide a short introduction and reason for your stay")])
