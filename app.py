from flask import Flask, render_template, request, flash, redirect, url_for
from data_models import db, Author, Book
import os
from datetime import datetime
import re

app = Flask(__name__)
# Set a secret key for Flask's flash messages
app.config['SECRET_KEY'] = 'a_very_secret_key_for_flash_messages'

# Determine the absolute path for consistent database location
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, 'data')
DATABASE_FILE_PATH = os.path.join(DATABASE_DIR, 'library.sqlite')

# Create the 'data' directory if it doesn't already exist
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)
    print(f"Created database directory: {DATABASE_DIR}")

# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_FILE_PATH}'

# Initialize SQLAlchemy with the Flask app
db.init_app(app)

# Create database tables if they don't exist
with app.app_context():
  db.create_all()
  print("Database tables created successfully!")

# --- Helper Functions for Validation and Redirection ---

def normalize_isbn(raw_isbn):
    """Removes non-digit characters from ISBN, converts to uppercase."""
    return re.sub(r'[^0-9X]', '', raw_isbn.upper())

def is_valid_isbn(isbn):
    """
    Validates the normalized ISBN length and 'X' placement.
    Returns (True, None) for valid ISBN, or (False, error_message_string) for invalid.
    """
    if len(isbn) == 13:
        if 'X' in isbn:
            return False, "Invalid ISBN: 13-digit ISBNs cannot contain 'X'."
    elif len(isbn) == 10:
        if 'X' in isbn[:-1]:
            return False, "Invalid ISBN: 'X' is only allowed as the last character for 10-digit ISBNs."
    else:
        return False, "ISBN must be 10 or 13 digits long after removing dashes/spaces."
    return True, None # ISBN is valid

def flash_and_redirect(message, category='error', endpoint='add_book'):
    """Flashes a message and redirects to a specified endpoint."""
    flash(message, category)
    return redirect(url_for(endpoint))

# --- End Helper Functions ---


# Route for adding authors
@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        # Retrieve form data
        author_name = request.form['name'].strip()
        birth_date_str = request.form.get('birth_date')
        death_date_str = request.form.get('date_of_death')

        # Parse dates, handling empty strings
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d') if birth_date_str else None
        date_of_death = datetime.strptime(death_date_str, '%Y-%m-%d') if death_date_str else None

        # Validation: Date of Death vs. Date of Birth
        if birth_date and date_of_death and date_of_death < birth_date:
            return flash_and_redirect("Date of death cannot be before the date of birth.", endpoint='add_author')

        # Create a new Author object
        new_author = Author(
            name=author_name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )

        try:
            # Add the new author to the database session
            db.session.add(new_author)
            # Commit the transaction to save the author to the database
            db.session.commit()
            return flash_and_redirect(f"Author '{author_name}' added successfully!", 'success', endpoint='add_author')
        except Exception as e:
            db.session.rollback() # Rollback in case of an error
            return flash_and_redirect(f"Error adding author: {e}", endpoint='add_author')

    # For GET requests or after POST, render the add_author.html template
    return render_template('add_author.html')

# Route for adding books
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        # Retrieve form data
        raw_isbn = request.form['isbn']
        title = request.form['title'].strip()
        publication_year = request.form.get('publication_year', type=int)
        author_id = request.form.get('author_id', type=int)

        # Normalize ISBN
        isbn = normalize_isbn(raw_isbn)

        # If ISBN becomes empty after normalization (e.g., "abc-def" -> "")
        if not isbn:
            return flash_and_redirect("Invalid ISBN: Please enter an ISBN containing digits (0-9) or 'X' (for ISBN-10).")

        # Basic validation for other required fields (title, author_id)
        if not title or not author_id:
            return flash_and_redirect("Title and Author are required fields.")

        # Enhanced ISBN Validation (now that we know it contains valid chars and is not empty)
        isbn_is_valid, isbn_error_message = is_valid_isbn(isbn)
        if not isbn_is_valid:
            return flash_and_redirect(isbn_error_message)

        # Check if author exists
        author = db.session.get(Author, author_id)
        if not author:
            return flash_and_redirect("Selected author does not exist.")

        # Create a new Book object
        new_book = Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            author_id=author_id
        )

        try:
            # Add the new book to the database session
            db.session.add(new_book)
            # Commit the transaction to save the book to the database
            db.session.commit()
            return flash_and_redirect(f"Book '{title}' by {author.name} (ISBN: {isbn}) added successfully!", 'success')
        except Exception as e:
            db.session.rollback() # Rollback in case of an error
            # Check for unique constraint violation (e.g., ISBN already exists)
            if 'UNIQUE constraint failed' in str(e):
                return flash_and_redirect("Error adding book: A book with this ISBN already exists.")
            else:
                return flash_and_redirect(f"Error adding book: {e}")

    # For GET requests or after POST, fetch all authors and the current year
    authors = Author.query.all()
    current_year = datetime.now().year
    return render_template('add_book.html', authors=authors, current_year=current_year)

# Route for deleting
@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    # Find the book to be deleted by its ID
    book_to_delete = db.session.get(Book, book_id)

    if not book_to_delete:
        flash("Book not found.", 'error')
        return redirect(url_for('home'))

    try:
        # Get the author associated with the book before deletion
        author_of_book = book_to_delete.author

        # Delete the book
        db.session.delete(book_to_delete)
        db.session.commit()
        flash(f"Book '{book_to_delete.title}' deleted successfully!", 'success')

        # Check if the author has any remaining books
        # After deleting the book, query to see if this author still has books
        remaining_books_by_author = Book.query.filter_by(author_id=author_of_book.id).count()

        if remaining_books_by_author == 0:
            # If no other books by this author, delete the author as well
            db.session.delete(author_of_book)
            db.session.commit()
            flash(f"Author '{author_of_book.name}' also deleted as they have no remaining books.", 'success')

    except Exception as e:
        db.session.rollback() # Rollback in case of any error during deletion
        flash(f"Error deleting book: {e}", 'error')

    return redirect(url_for('home'))

# Route for homepage
@app.route('/')
def home():
    # Get sort_by parameter from URL query string, default to 'title'
    sort_by = request.args.get('sort_by', 'title')
    # Get search_query parameter from URL query string
    search_query = request.args.get('query', '').strip()
    # New: Get search_type parameter from URL query string, default to 'title'
    search_type = request.args.get('search_type', 'title')

    # Start with a base query for all books
    books_query = Book.query

    # Apply search filter if a query is provided
    if search_query:
        if search_type == 'author': # Check if search type is author
            books_query = books_query.join(Author).filter(Author.name.ilike(f'%{search_query}%'))
        else: # Default to 'title' search if no type or type is 'title'
            books_query = books_query.filter(Book.title.ilike(f'%{search_query}%'))


    # Apply sorting
    if sort_by == 'author':
        # Join with Author model to access author.name for sorting
        books = books_query.join(Author).order_by(Author.name).all()
    else: # Default or 'title'
        books = books_query.order_by(Book.title).all()

    # Pass books data, current sort_by, search_query, and search_type to the template
    return render_template('home.html',
                           books=books,
                           sort_by=sort_by,
                           search_query=search_query,
                           search_type=search_type) # Pass search_type to template


# Run the Flask development server
if __name__ == '__main__':
    app.run(debug=True, port=5001)