from flask_wtf import FlaskForm

from wtforms import DateField, IntegerField, StringField, EmailField


class BookingForm(FlaskForm):
    checkin = DateField()
    checkout = DateField()
    guests = IntegerField()
    first_name = StringField()
    last_name = StringField()
    email = EmailField()
    phone = StringField()
