from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)

    # Establishes a one-to-many relationship with Book.
    # Allows: author.books -> list of books written by the author.
    # Enables cascading deletes (deleting an author removes their books).
    books = db.relationship('Book',
                            back_populates='author',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Author id={self.id} name='{self.name}'>"

    def __str__(self):
        birth = self.birth_date.strftime('%Y-%m-%d') if self.birth_date else "Unknown"
        death = self.date_of_death.strftime('%Y-%m-%d') if self.date_of_death else "Unknown"
        return f"{self.name} (b. {birth}) - (d. {death})"



class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(60), nullable=False)
    publication_year = db.Column(db.Integer)
 
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    # Establishes the inverse side of the relationship with Author.
    # Allows: book.author -> the author instance of the book.
    # Enables access like book.author.name.
    author = db.relationship('Author', back_populates='books')

    def __repr__(self):
        return f"<Book id={self.id} title='{self.title}' isbn={self.isbn}>"
    
    def __str__(self):
        return f"'{self.title}' published in {self.publication_year if self.publication_year else 'Unknown'}"
