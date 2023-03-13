from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.sql import func

from libreproperty.db import db
from libreproperty.models import Listing, Booking, Message


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(200), primary_key=False, unique=False, nullable=False)
    name = db.Column(db.String, nullable=True)
    email_verified = db.Column(db.Boolean, unique=False, default=False)
    created_on = db.Column(db.DateTime, index=False, unique=False, nullable=True, server_default=func.now())
    last_login = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    listings = db.relationship("Listing", back_populates="user")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(
            password,
            method='sha256'
        )

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    @property
    def bookings(self):
        return db.session.execute(
            db.select(Booking).join(Listing).filter_by(user_id=self.id).join(User)
            .order_by(Booking.created_on.desc()).limit(10)
        ).scalars().all()

    @property
    def messages(self):
        return db.session.execute(
            db.select(Message).join(Listing).filter_by(user_id=self.id).join(User)
            .order_by(Message.created_on.desc()).limit(10)
        ).scalars().all()
