from app import app, db
from data_models import Author, Book
from datetime import date
import re
from sqlalchemy.exc import IntegrityError

# Helper function for ISBN normalization
def normalize_isbn(raw_isbn):
    return re.sub(r'[^0-9X]', '', raw_isbn.upper())

with app.app_context():
    # --- Authors to Add ---
    authors_data = [
        {'name': 'J.R.R. Tolkien', 'birth_date': date(1892, 1, 3), 'date_of_death': date(1973, 9, 2)},
        {'name': 'Jane Austen', 'birth_date': date(1775, 12, 16), 'date_of_death': date(1817, 7, 18)},
        {'name': 'George Orwell', 'birth_date': date(1903, 6, 25), 'date_of_death': date(1950, 1, 21)},
        {'name': 'Agatha Christie', 'birth_date': date(1890, 9, 15), 'date_of_death': date(1976, 1, 12)},
        {'name': 'Stephen King', 'birth_date': date(1947, 9, 21), 'date_of_death': None},
        {'name': 'Mary Shelley', 'birth_date': date(1797, 8, 30), 'date_of_death': date(1851, 2, 1)},
        {'name': 'Leo Tolstoy', 'birth_date': date(1828, 9, 9), 'date_of_death': date(1910, 11, 20)},
        {'name': 'Virginia Woolf', 'birth_date': date(1882, 1, 25), 'date_of_death': date(1941, 3, 28)},
        {'name': 'H.P. Lovecraft', 'birth_date': date(1890, 8, 20), 'date_of_death': date(1937, 3, 15)},
        {'name': 'Gabriel Garcia Marquez', 'birth_date': date(1927, 3, 6), 'date_of_death': date(2014, 4, 17)},
    ]

    authors_obj = {} # To store author objects for linking to books
    for auth_data in authors_data:
        # Check if author already exists to avoid creating duplicate Author *objects*
        # This is the simplest way to get the correct Author object for linking books.
        author = Author.query.filter_by(name=auth_data['name']).first()
        if not author:
            author = Author(**auth_data)
            db.session.add(author)
        authors_obj[auth_data['name']] = author

    # Commit authors first so their IDs are available for books
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Warning: Could not add some authors (they might already exist): {e}")


    # --- Books to Add ---
    books_data = [
        {'isbn': '978-0-618-26027-4', 'title': 'The Fellowship of the Ring', 'publication_year': 1954, 'author_name': 'J.R.R. Tolkien'},
        {'isbn': '9780345339683', 'title': 'The Two Towers', 'publication_year': 1954, 'author_name': 'J.R.R. Tolkien'},
        {'isbn': '978-0-345-34042-4', 'title': 'The Return of the King', 'publication_year': 1955, 'author_name': 'J.R.R. Tolkien'},
        {'isbn': '9780141439518', 'title': 'Pride and Prejudice', 'publication_year': 1813, 'author_name': 'Jane Austen'},
        {'isbn': '9780141439594', 'title': 'Sense and Sensibility', 'publication_year': 1811, 'author_name': 'Jane Austen'},
        {'isbn': '978-0-452-28423-4', 'title': '1984', 'publication_year': 1949, 'author_name': 'George Orwell'},
        {'isbn': '9780451524935', 'title': 'Animal Farm', 'publication_year': 1945, 'author_name': 'George Orwell'},
        {'isbn': '978-0007119339', 'title': 'And Then There Were None', 'publication_year': 1939, 'author_name': 'Agatha Christie'},
        {'isbn': '978-0007120618', 'title': 'The Murder of Roger Ackroyd', 'publication_year': 1926, 'author_name': 'Agatha Christie'},
        {'isbn': '9780345453747', 'title': 'It', 'publication_year': 1986, 'author_name': 'Stephen King'},
        {'isbn': '0451167733', 'title': 'The Shining', 'publication_year': 1977, 'author_name': 'Stephen King'},
        {'isbn': '9780486282124', 'title': 'Frankenstein', 'publication_year': 1818, 'author_name': 'Mary Shelley'},
        {'isbn': '9780140447934', 'title': 'War and Peace', 'publication_year': 1869, 'author_name': 'Leo Tolstoy'},
        {'isbn': '9780156030062', 'title': 'Mrs Dalloway', 'publication_year': 1925, 'author_name': 'Virginia Woolf'},
        {'isbn': '9780486295322', 'title': 'The Call of Cthulhu and Other Weird Stories', 'publication_year': 1928, 'author_name': 'H.P. Lovecraft'},
        {'isbn': '9780060883287', 'title': 'One Hundred Years of Solitude', 'publication_year': 1967, 'author_name': 'Gabriel Garcia Marquez'},
    ]

    for book_data in books_data:
        normalized_isbn = normalize_isbn(book_data['isbn'])
        author_obj = authors_obj.get(book_data['author_name']) # Get the Author object from our dict

        if not author_obj:
            print(f"Warning: Author '{book_data['author_name']}' not found for book '{book_data['title']}'. Skipping.")
            continue

        # Add the book directly
        new_book = Book(
            isbn=normalized_isbn,
            title=book_data['title'],
            publication_year=book_data['publication_year'],
            author=author_obj # Link directly via object
        )
        db.session.add(new_book)

    try:
        db.session.commit()
        print("All new authors and books committed successfully!")
    except IntegrityError as e:
        db.session.rollback()
        print(f"Error: Could not commit all books. Some entries (likely duplicate ISBNs) already exist.")
    except Exception as e:
        db.session.rollback()
        print(f"An unexpected error occurred during book commit: {e}")

    print("--- Data Seeding Attempt Complete ---")