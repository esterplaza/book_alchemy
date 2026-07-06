
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)

    def __str__(self):
        return f"Author's name: {self.name}"

    def __repr__(self):
        return f"<Author {self.id}: {self.name}, birthdate: {self.birth_date}, date of death: {self.date_of_death}>"


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(17), unique=True)
    title = db.Column(db.String(100))
    publication_year = db.Column(db.Date)
    author_id = db.Column(
        db.Integer,
        db.ForeignKey("authors.id"))


