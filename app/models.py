from app import db
from datetime import datetime
import pytz  # Add pytz for timezone conversion
from sqlalchemy.dialects.mysql import LONGBLOB  # Import for storing binary data


def current_ist_time():
    """Helper function to get the current time in IST."""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)  # Use current IST time


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('Super Admin', 'Admin', 'User'), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    # Relationship to borrowed books
    borrowed_books = db.relationship('BorrowedBook', backref='borrower', lazy='dynamic')


class Book(db.Model):
    __tablename__ = 'books'
    title = db.Column(db.String(255), primary_key=True)
    author = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)  # Indicates if the book is marked as deleted
    deleted_by_admin = db.Column(db.String(255), nullable=True)  # Stores the admin username who deleted the book
    cover_image = db.Column(LONGBLOB, nullable=True)  # New column for storing the cover image as binary data

    # Relationship to borrowed books
    borrowed_books = db.relationship('BorrowedBook', backref='associated_book', lazy='joined')


class BorrowedBook(db.Model):
    __tablename__ = 'borrowed_books'
    id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String(255), db.ForeignKey('books.title', ondelete="CASCADE"), nullable=False)
    borrowed_by_user = db.Column(db.String(255), db.ForeignKey('users.username', ondelete="CASCADE"), nullable=False)
    borrow_date = db.Column(db.DateTime, default=current_ist_time)  # Use IST time for the default value
    return_date = db.Column(db.DateTime, nullable=True)

    # Relationship for easy access to the associated book
    book = db.relationship('Book', backref=db.backref('borrowed_books_list', lazy='dynamic'))
