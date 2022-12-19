from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_user

from libreproperty import db
from .forms import SignupForm, LoginForm
from .models import User

auth_bp = Blueprint('auth_bp', __name__, template_folder='templates')


@auth_bp.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user is None:
            user = User(
                name=form.name.data,
                email=form.email.data,
                password=form.password.data
            )
            db.session.add(user)
            db.session.commit()  # Create new user
            login_user(user)  # Log in as newly created user
            return redirect(url_for('pages_bp.index'))
        flash('A user already exists with that email address.')
    return render_template('auth/signup.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html', form=LoginForm())
