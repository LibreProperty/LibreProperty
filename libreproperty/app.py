import os

from flask import Flask, flash, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from libreproperty.auth import auth_bp, User
from libreproperty.pages import pages_bp
from libreproperty.dashboard import dashboard_bp
from libreproperty import models

login_manager = LoginManager()
login_manager.login_view = "auth_bp.login"


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_bp.login'))


def environ_get_bool(name: str) -> bool:
    return os.getenv(name, 'False').lower() in ('true', '1', 't')


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE", "sqlite:///project.db")
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", os.urandom(32))
    # Minio endpoint or `aws`
    app.config['S3_ENDPOINT'] = os.environ.get("S3_ENDPOINT", "http://localhost:9000")
    app.config['S3_VERIFY'] = environ_get_bool("S3_VERIFY")
    app.config['BUCKET'] = os.environ.get("BUCKET", "libreproperty-images")
    CSRFProtect(app)
    app.register_blueprint(auth_bp)
    login_manager.init_app(app)
    app.register_blueprint(pages_bp)
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    from libreproperty import db
    db.init_app(app)
    with app.app_context():
        db.create_all()
        users = User.query.all()
        print(users)
        return app
