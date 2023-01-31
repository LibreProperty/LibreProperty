import datetime

from libreproperty.models import Photo, Listing, Booking
from libreproperty.auth.models import User


def test_photo_bucket_key():
    photo = Photo()
    photo.location = "s3://mybucket-1/my-key-1"
    assert photo.bucket == "mybucket-1"
    assert photo.object_key == "my-key-1"

    photo.location = "s3://b/4-bryi-Screenshot_from_2022-12-07_12-13-58.png"
    assert photo.bucket == "b"
    assert photo.object_key == "4-bryi-Screenshot_from_2022-12-07_12-13-58.png"


def test_booking_weekend_nights():
    booking = Booking()
    booking.checkin = datetime.date(year=2023, month=1, day=1)
    booking.checkout = datetime.date(year=2023, month=1, day=2)
    assert booking.nights == 1
    assert booking.weekend_nights == 0
    booking.checkin = datetime.date(year=2023, month=1, day=6)
    booking.checkout = datetime.date(year=2023, month=1, day=7)
    assert booking.nights == 1
    assert booking.weekend_nights == 1


def test_listing_cost_calculation():
    listing = Listing()
    listing.base_price = 50
    assert listing.cost_cents(2, 0) == 100 * 100
    assert listing.cost_cents(7, 0) == 7 * 50 * 100
    listing.weekly_price_factor = 0.80
    assert listing.cost_cents(7, 0) == 7 * 50 * 100 * 0.8
    assert listing.cost_cents(6, 0) == 6 * 50 * 100
    listing.monthly_price_factor = 0.70
    assert listing.cost_cents(30, 0) == 30 * 50 * 100 * 0.7
    listing.cleaning_fee = 150

    assert listing.cost_cents(30, 0) == ((30 * 50 * 100) + 150 * 100) * 0.7

    listing.weekend_price = 100
    assert listing.cost_cents(3, 1) == (150 * 100) + (2 * 50 * 100) + (100 * 100)
