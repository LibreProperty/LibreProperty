import os

from flask import Flask
from flask_login import LoginManager

from libreproperty.auth import auth_bp, User
from libreproperty.pages import pages_bp

login_manager = LoginManager()


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


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config['SECRET_KEY'] = os.urandom(32)
    app.register_blueprint(auth_bp)
    login_manager.init_app(app)
    app.register_blueprint(pages_bp)
    from libreproperty import db
    db.init_app(app)
    with app.app_context():
        db.create_all()
        users = User.query.all()
        print(users)
        return app