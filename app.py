import os
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from data_models import db, Author

app = Flask(__name__)

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
app.config['SECRET_KEY'] = 'a_very_secret_key_for_flash_messages'

# Initialize SQLAlchemy with the Flask app
db.init_app(app)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        # Retrieve form data
        author_name = request.form['name']
        birth_date_str = request.form.get('birth_date')
        death_date_str = request.form.get('date_of_death')

        # Parse dates, handling empty strings
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d') if birth_date_str else None
        date_of_death = datetime.strptime(death_date_str, '%Y-%m-%d') if death_date_str else None

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
            flash(f"Author '{author_name}' added successfully!", 'success')
            # Redirect to the same page to clear form submission and display message
            return redirect(url_for('add_author'))
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            flash(f"Error adding author: {e}", 'error')

    # For GET requests or after POST, render the add_author.html template
    return render_template('add_author.html')


# Run the Flask development server
if __name__ == '__main__':
    app.run(debug=True)
