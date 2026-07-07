import os
from data_models import db, Author, Book
from datetime import date
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
db.init_app(app)


@app.route('/add_author', methods=["GET", "POST"])
def add_author():
    """Adds a new author to the database.

    GET request: renders the add_author.html form used to gather information
                about an author.
    POST request: adds a new author record to the database using SQLAlchemy.

    Returns:
        The rendered HTML of the add post form on GET.
        A success message on successful POST.
    """
    if request.method == "POST":
        date_of_death_str = request.form["date_of_death"]
        try:
            birth_date = date.fromisoformat(request.form["birthdate"])
            if date_of_death_str:
                date_of_death = date.fromisoformat(date_of_death_str)
            else:
                date_of_death = None
        except ValueError:
            return "Dates must be in YYYY-MM-DD format.", 400
        author = Author(
            name=request.form["name"],
            birth_date=birth_date,
            date_of_death=date_of_death
        )
        db.session.add(author)
        db.session.commit()
        return render_template(
            "add_author.html",
            success=f"The author {author.name} has successfully been added to the database"
        ), 200
    return render_template("add_author.html")

@app.route('/add_book', methods=["GET", "POST"])
def add_book():
    """Adds a new book to the database.

    GET request: renders the add_book.html form used to gather information
                about a book.
    POST request: adds a new book record to the database using SQLAlchemy.

    Returns:
        The rendered HTML of the add post form on GET.
        A success message on successful POST.
    """
    authors = db.session.execute(db.select(Author).order_by(Author.name)).scalars().all()
    if request.method == "POST":
        try:
            publication_year = int(request.form["publication_year"])
        except ValueError:
            return {"error": "Please enter a valid year."}, 400
        book = Book(
            title=request.form["title"],
            isbn=request.form["isbn"],
            publication_year=publication_year,
            author_id=request.form["author_id"]
        )
        db.session.add(book)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"error": "A book with that ISBN already exists."}, 400
        return render_template(
            "add_book.html",
            authors=authors,
            success=f"The book {book.title} has successfully been added to the database"
        ), 200
    return render_template("add_book.html", authors=authors)


# with app.app_context():
#     db.create_all()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)