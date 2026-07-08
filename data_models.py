
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """
       A class used to represent an author of a book

       Attributes
       ----------
       id : int
           Primary key, auto-incrementing
       name : str
           the name of the author
       birth_date : str
           the birthdate of the author
       date_of_death: str
           date of death, Null if the author still alive
       """
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.String(10))
    date_of_death = db.Column(db.String(10))

    def __str__(self):
        """
        Return a user-friendly string that represents the author
        """
        return f"Author's name: {self.name} (Author ID: {self.id}"

    def __repr__(self):
        """
        Return a readable string that represents the author
        """
        return (f"<Author {self.id}: {self.name}, birthdate: {self.birth_date},"
                f" date of death: {self.date_of_death}>")


class Book(db.Model):
    """
       A class used to represent a book

       Attributes
       ----------
       id : int
           Primary key, auto-incrementing
       isbn : str
           ISBN identifier
       title : str
           the book title
       publication_year: int
           the year the book was published
       author_id: int
           Foreign key referencing the author. If the author is unknown the author_id will be null.
       """
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(17), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer)
    author_id = db.Column(
        db.Integer,
        db.ForeignKey("authors.id"),
        nullable=True)

    def __str__(self):
        """
        Return a user-friendly string that represents the author
        """
        return f"Books's title: {self.title} (Book ID: {self.id})"

    def __repr__(self):
        """
        Return a readable string that represents the author
        """
        return (f"<Book {self.id}: {self.title}, ISBN: {self.isbn},"
                f" publication year: {self.publication_year}"
                f" (Author ID: {self.author_id})>")
