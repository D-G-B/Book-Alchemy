from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from data_models import db
import os

app = Flask(__name__)

# Get the absolute path to the directory where this script is located
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the full path for the database directory and file
DATABASE_DIR = os.path.join(BASE_DIR, 'data')
DATABASE_FILE_PATH = os.path.join(DATABASE_DIR, 'library.sqlite')

# Ensure the database directory exists
# Create it if it doesn't.
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)
    print(f"Created database directory: {DATABASE_DIR}")

# Configure the Flask app to use the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_FILE_PATH}'

# Initialize the SQLAlchemy database instance with the Flask app
db.init_app(app)

# Create database tables within the application context
# This block runs when the app is loaded, ensuring tables exist.
with app.app_context():
  db.create_all()
  print("Database tables created successfully!")

# Run the Flask development server if the script is executed directly
if __name__ == '__main__':
    app.run(debug=True)
