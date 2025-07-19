from flask import Blueprint, render_template, redirect, flash, url_for, request
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST','GET'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        check_username = User.query.filter_by(username=username).first()

        if check_username:
            if check_password_hash(check_username.password, password):
                flash('Login Sucessfully', category='success')
                login_user(check_username, remember=True)
                return redirect(url_for('views.dashboard'))
            else:
                flash('Incorrect Password', category='error')
        else:
                flash('Email or Username Does not Exist', category='error')
            
    return render_template("system/login.html")


@auth.route('/register', methods=['POST','GET'])
def register():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        check_username = User.query.filter_by(username=username).first()

        if check_username:
            flash('username is already exist', category='error')
        elif password != password2:
            flash('password does not match', category='error')

        else:
            new_user = User(
                            username=username,
                            password=generate_password_hash(password,method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()

            flash('username Successfully Created', category='success')

            return redirect(url_for('auth.login'))

    return render_template('system/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home')) 