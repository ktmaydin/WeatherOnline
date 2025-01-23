from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_required, login_user, logout_user, current_user


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Erfolgreich eingeloggt!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Falsches Passwort!',category='error')
        else:
            flash('E-Mail existiert nicht!', category='error')
        
    return render_template("accounts/login.html", user = current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=["GET","POST"])
def sign_up():
    if request.method == 'POST' :
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('E-Mail existiert bereits!', category='error')        
        elif len(email) < 4:
            flash('E-Mail muss mehr als vier Buchstaben enthalten!', category='error')
        elif len(first_name) < 2:
            flash('Vorname muss mehr als einen Buchstaben enthalten!' , category ='error')
        elif (password1 != password2):
            flash('Passwörter stimmen nicht überein!', category='error')
        elif len(password1) < 7:
            flash('Passwort muss mehr als 7 Buchstaben enthalten', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account erstellet', category='success') 
            return redirect(url_for('views.home'))
    
    return render_template("accounts/sign_up.html", user = current_user)
