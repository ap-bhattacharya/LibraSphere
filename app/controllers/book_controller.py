import re
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, send_file
from app.models import Book, BorrowedBook
from app import db
from datetime import datetime
import io

book_blueprint = Blueprint('book', __name__, url_prefix='/books')

# Validation functions
def is_valid_name(name):
    """Validate names to allow alphanumeric characters, spaces, and optional hyphens."""
    return bool(re.match(r"^[A-Za-z0-9]+(?:[ -][A-Za-z0-9]+)*$", name))

def is_valid_author_or_genre(value):
    """Validate author and genre to allow only alphabetic characters, spaces, and optional hyphens."""
    return bool(re.match(r"^[A-Za-z]+(?:[ -][A-Za-z]+)*$", value))

@book_blueprint.route('/dashboard')
def dashboard():
    if 'role' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html', username=session['username'], role=session['role'], name=session['name'])

@book_blueprint.route('/manage', methods=['GET'])
def manage_books():
    if 'role' not in session:
        return redirect(url_for('auth.login'))

    search_query = request.args.get('search_query', '')
    page = request.args.get('page', 1, type=int)  # Get the current page number, default is 1
    per_page = 10  # Number of books per page

    books_query = Book.query.filter_by(deleted=0)  # Only show non-deleted books

    if search_query:
        books_query = books_query.filter(
            (Book.title.ilike(f"%{search_query}%")) |
            (Book.author.ilike(f"%{search_query}%")) |
            (Book.publication_year.ilike(f"%{search_query}%")) |
            (Book.genre.ilike(f"%{search_query}%"))
        )

    # Paginate the books query
    pagination = books_query.paginate(page=page, per_page=per_page, error_out=False)
    books = pagination.items  # Books for the current page

    # Get borrowed books
    borrowed_books = BorrowedBook.query.filter(BorrowedBook.return_date == None).order_by(BorrowedBook.borrow_date.desc()).all()
    borrowed_titles = [borrowed.book_title for borrowed in borrowed_books]

    return render_template(
        'manage_books.html',
        books=books,
        borrowed_books=borrowed_books,
        borrowed_titles=borrowed_titles,
        role=session.get('role'),
        pagination=pagination,  # Pass pagination object to template
        search_query=search_query  # Keep the search query for rendering
    )

@book_blueprint.route('/borrow/<string:title>', methods=['POST'])
def borrow_book(title):
    if 'role' not in session or session['role'] != 'User':
        return redirect(url_for('auth.login'))

    book = Book.query.filter_by(title=title, deleted=0).first()
    if not book:
        flash("Book not found or marked as deleted.", "danger")
        return redirect(url_for('book.manage_books'))

    # Check if the book is already borrowed
    borrowed = BorrowedBook.query.filter_by(book_title=title, return_date=None).first()
    if borrowed:
        flash("This book is already borrowed by another user.", "danger")
        return redirect(url_for('book.manage_books'))

    # Borrow the book
    borrowed_book = BorrowedBook(book_title=title, borrowed_by_user=session['username'])
    db.session.add(borrowed_book)
    db.session.commit()
    flash("Book borrowed successfully.", "success")
    return redirect(url_for('book.manage_books'))

@book_blueprint.route('/borrowed', methods=['GET'])
def borrowed_books():
    if 'role' not in session or session['role'] not in ['Admin', 'Super Admin']:
        return redirect(url_for('auth.login'))

    # Retrieve all borrowed books sorted by most recent borrow date
    borrowed_books = BorrowedBook.query.order_by(BorrowedBook.borrow_date.desc()).all()
    return render_template('borrowed_books.html', borrowed_books=borrowed_books)

@book_blueprint.route('/return/<int:id>', methods=['POST'])
def return_book(id):
    if 'role' not in session or session['role'] != 'User':
        return redirect(url_for('auth.login'))

    borrowed_book = BorrowedBook.query.get(id)
    if not borrowed_book or borrowed_book.borrowed_by_user != session['username']:
        flash("You cannot return a book that you haven't borrowed.", "danger")
        return redirect(url_for('book.user_borrowed_books'))

    # Return the book
    borrowed_book.return_date = datetime.now()
    db.session.commit()
    flash("Book returned successfully.", "success")
    return redirect(url_for('book.user_borrowed_books'))

@book_blueprint.route('/user_borrowed_books', methods=['GET', 'POST'])
def user_borrowed_books():
    """Page for Users to view and return borrowed books."""
    if 'role' not in session or session['role'] != 'User':
        return redirect(url_for('auth.login'))

    username = session['username']

    # Use a query that joins with the Book model
    borrowed_books = BorrowedBook.query.filter_by(borrowed_by_user=username, return_date=None) \
                                       .join(Book, BorrowedBook.book_title == Book.title) \
                                       .options(db.contains_eager(BorrowedBook.associated_book)) \
                                       .order_by(BorrowedBook.borrow_date.desc()).all()

    if request.method == 'POST':
        # Handle book return
        book_title = request.form.get('book_title')
        borrowed_record = BorrowedBook.query.filter_by(book_title=book_title, borrowed_by_user=username, return_date=None).first()

        if borrowed_record:
            borrowed_record.return_date = datetime.now()
            db.session.commit()
            flash(f"Book '{book_title}' returned successfully.", "success")
        else:
            flash("Error returning book.", "danger")

        return redirect(url_for('book.user_borrowed_books'))

    return render_template('borrowed_books_user.html', borrowed_books=borrowed_books)

@book_blueprint.route('/deleted', methods=['GET'])
def deleted_books():
    if 'role' not in session or session['role'] != 'Super Admin':
        return redirect(url_for('auth.login'))

    search_query = request.args.get('search_query')
    books = Book.query.filter_by(deleted=1)  # Only show deleted books

    if search_query:
        books = books.filter(
            (Book.title.ilike(f"%{search_query}%")) |
            (Book.author.ilike(f"%{search_query}%")) |
            (Book.publication_year.ilike(f"%{search_query}%")) |
            (Book.genre.ilike(f"%{search_query}%"))
        )

    books = books.all()
    return render_template('deleted_books.html', books=books)

@book_blueprint.route('/add', methods=['GET', 'POST'])
def add_book():
    if 'role' not in session or session['role'] not in ['Admin', 'Super Admin']:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')
        year = request.form.get('year')
        cover_image = request.files.get('cover_image')

        has_error = False
        if not is_valid_name(title):
            session['title_error'] = "Invalid title. Titles can only contain alphanumeric characters, spaces, and hyphens."
            has_error = True
        if not is_valid_author_or_genre(author):
            session['author_error'] = "Author name must start with alphabets, can contain spaces, and must not contain numbers."
            has_error = True
        if not year.isdigit() or not (1000 <= int(year) <= 9999):
            session['year_error'] = "Invalid publication year. Please enter a valid 4-digit year."
            has_error = True
        if not is_valid_author_or_genre(genre):
            session['genre_error'] = "Invalid genre. It must not contain numbers and can include spaces."
            has_error = True

        if has_error:
            return redirect(url_for('book.add_book'))

        cover_image_data = cover_image.read() if cover_image else None

        new_book = Book(title=title, author=author, genre=genre, publication_year=year, cover_image=cover_image_data)
        db.session.add(new_book)
        db.session.commit()
        flash("Book added successfully.", "success")
        return redirect(url_for('book.manage_books'))

    return render_template('add_book.html')

@book_blueprint.route('/delete/<string:title>', methods=['POST'])
def delete_book(title):
    if 'role' not in session or session['role'] not in ['Admin', 'Super Admin']:
        return redirect(url_for('auth.login'))

    book = Book.query.filter_by(title=title, deleted=0).first()
    if book:
        book.deleted = 1
        book.deleted_by_admin = session['username']
        db.session.commit()
        flash("Book deleted successfully. It is now visible in the Deleted Books section.", "success")
    else:
        flash("Book not found or already deleted.", "danger")
    return redirect(url_for('book.manage_books'))

@book_blueprint.route('/retrieve/<string:title>', methods=['POST'])
def retrieve_book(title):
    if 'role' not in session or session['role'] != 'Super Admin':
        return redirect(url_for('auth.login'))

    book = Book.query.filter_by(title=title, deleted=1).first()
    if book:
        book.deleted = 0
        book.deleted_by_admin = None
        db.session.commit()
        flash("Book retrieved successfully.", "success")
    else:
        flash("Book not found or already retrieved.", "danger")
    return redirect(url_for('book.deleted_books'))

@book_blueprint.route('/permanently_delete/<string:title>', methods=['POST'])
def permanently_delete_book(title):
    if 'role' not in session or session['role'] != 'Super Admin':
        return redirect(url_for('auth.login'))

    book = Book.query.filter_by(title=title, deleted=1).first()
    if book:
        db.session.delete(book)
        db.session.commit()
        flash("Book permanently deleted successfully.", "success")
    else:
        flash("Book not found or already permanently deleted.", "danger")
    return redirect(url_for('book.deleted_books'))

@book_blueprint.route('/update/<string:title>', methods=['GET', 'POST'])
def update_book(title):
    if 'role' not in session or session['role'] not in ['Admin', 'Super Admin']:
        return redirect(url_for('auth.login'))

    book = Book.query.filter_by(title=title, deleted=0).first()

    if not book:
        flash("Book not found or is marked as deleted.", "danger")
        return redirect(url_for('book.manage_books'))

    if request.method == 'POST':
        author = request.form.get('author')
        year = request.form.get('year')
        genre = request.form.get('genre')
        cover_image = request.files.get('cover_image')

        if not is_valid_author_or_genre(author):
            flash("Invalid author name. It must not contain numbers and can include spaces or hyphens.", "danger")
            return render_template('update_book.html', book=book)

        if not year.isdigit() or not (1000 <= int(year) <= 9999):
            flash("Invalid publication year. Enter a valid 4-digit year.", "danger")
            return render_template('update_book.html', book=book)

        if not is_valid_author_or_genre(genre):
            flash("Invalid genre. It must not contain numbers and can include spaces or hyphens.", "danger")
            return render_template('update_book.html', book=book)

        book.author = author
        book.publication_year = int(year)
        book.genre = genre

        if cover_image:
            book.cover_image = cover_image.read()

        db.session.commit()
        flash("Book updated successfully.", "success")
        return redirect(url_for('book.manage_books'))

    return render_template('update_book.html', book=book)

@book_blueprint.route('/cover_image/<string:title>')
def get_cover_image(title):
    """Serve the cover image for a book."""
    book = Book.query.filter_by(title=title).first()
    if book and book.cover_image:
        return send_file(
            io.BytesIO(book.cover_image),
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=f"{title}_cover.jpg"
        )
    return "", 404  # Return 404 if image is not found
