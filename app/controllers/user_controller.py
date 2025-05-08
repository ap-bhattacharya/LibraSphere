import re
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.models import User, BorrowedBook  # Ensure BorrowedBook model is imported
from app import db
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

user_blueprint = Blueprint('user', __name__, url_prefix='/users')

def is_valid_name(name):
    """Validate name: must start with alphabets, can contain spaces, cannot contain numbers."""
    return bool(re.match(r"^[A-Za-z]+(?: [A-Za-z]+)*$", name))

def is_valid_username(username):
    """Validate username: must start with alphabet or number, can contain numbers, no spaces, not only numbers."""
    return bool(re.match(r"^(?=.*[A-Za-z])[A-Za-z0-9]+$", username))

@user_blueprint.route('/manage', methods=['GET', 'POST'])
def manage_users():
    if 'role' not in session or session['role'] not in ['Super Admin']:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # Existing code for adding a user
        pass

    # Fetch users excluding Super Admin
    users = User.query.filter(User.role != 'Super Admin').all()
    return render_template('manage_users.html', users=users, role=session.get('role'))

@user_blueprint.route('/add', methods=['GET', 'POST'])
def add_user():
    if 'role' not in session or session['role'] != 'Super Admin':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        # Backend validation
        if not is_valid_name(name):
            flash("Invalid name. Name must start with alphabets and can contain spaces but cannot contain numbers.", "danger")
            return redirect(url_for('user.add_user'))

        if not is_valid_username(username):
            flash("Invalid username. Username must start with an alphabet or number, can contain numbers, but cannot have spaces or be only numbers.", "danger")
            return redirect(url_for('user.add_user'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_user = User(name=name, username=username, password=hashed_password, role=role)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("User added successfully.", "success")
        except IntegrityError:
            db.session.rollback()
            flash("Username already exists. Please choose a different one.", "danger")

        return redirect(url_for('user.add_user'))

    return render_template('add_user.html')

@user_blueprint.route('/delete/<int:id>', methods=['POST'])
def delete_user(id):
    if 'role' not in session or session['role'] != 'Super Admin':
        return redirect(url_for('auth.login'))

    user = User.query.get(id)
    if user:
        # Step 1: Update borrowed_books where the user has borrowed books
        borrowed_books = BorrowedBook.query.filter_by(borrowed_by_user=user.username).all()
        for book in borrowed_books:
            book.borrowed_by_user = None  # Or assign a default value like 'No User'
            db.session.commit()  # Commit the changes to the borrowed_books table

        # Step 2: Now, delete the user from the database
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", "success")
    else:
        flash("User not found.", "danger")
    return redirect(url_for('user.manage_users'))

@user_blueprint.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if 'role' not in session or session['role'] != 'Super Admin':
        return redirect(url_for('auth.login'))

    user = User.query.get(id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('user.manage_users'))

    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        role = request.form.get('role')

        # Backend validation
        if not is_valid_name(name):
            flash("Invalid name. Name must start with alphabets and can contain spaces but cannot contain numbers.", "danger")
            return redirect(url_for('user.edit_user', id=id))

        if not is_valid_username(username):
            flash("Invalid username. Username must start with an alphabet or number, can contain numbers, but cannot have spaces or be only numbers.", "danger")
            return redirect(url_for('user.edit_user', id=id))

        # Update user details
        user.name = name
        user.username = username
        user.role = role
        db.session.commit()
        flash("User updated successfully.", "success")
        return redirect(url_for('user.manage_users'))

    return render_template('edit_user.html', user=user)
