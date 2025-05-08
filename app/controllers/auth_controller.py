from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db

auth_blueprint = Blueprint('auth', __name__)

# Root URL route to redirect to login
@auth_blueprint.route('/')
def index():
    print("Root route accessed")
    return redirect(url_for('auth.login'))


# Login route
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = username
            session['role'] = user.role
            session['name'] = user.name
            flash(f"Welcome {user.name}! You are logged in as {user.role}.", 'success')
            return redirect(url_for('book.dashboard'))
        else:
            flash("Invalid username or password", 'danger')
    return render_template('login.html')

# Logout route
@auth_blueprint.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", 'info')
    return redirect(url_for('auth.login'))

# Signup route
@auth_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose a different one.", 'danger')
            return redirect(url_for('auth.signup'))

        # Create a new user with the role 'User'
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role='User', name=name)
        db.session.add(new_user)
        db.session.commit()
        flash("User registered successfully. Please log in.", 'success')
        return redirect(url_for('auth.login'))
    return render_template('signup.html')
