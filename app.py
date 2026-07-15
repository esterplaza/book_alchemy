import os
import time
from datetime import date

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from data_models import db, Author, Book

load_dotenv()
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
db.init_app(app)


def get_cover_url(isbn):
    """
    Get the cover URL from Google Books API.
    Retries up to 4 times if Google returns a 503 error.
    Returns None if no cover is available or the request fails.
    """
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={API_KEY}"
    attempts = 4
    for attempt in range(1, attempts):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 503:
                if attempt < (attempts - 1):
                    time.sleep(5)
                    continue
                return None
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            if items:
                volume_info = items[0].get("volumeInfo", {})
                image_links = volume_info.get("imageLinks", {})
                return image_links.get("thumbnail")
            return None
        except (requests.Timeout, requests.RequestException, KeyError, IndexError, TypeError):
            return None
    return None


def get_books_data(books):
    """
    Given the Isbn, requests from the API google books the cover url.
    creates a list with title, author (from books) and cover url (from API).
    :param
        books: A list of tuples (SQLAlchemy Rows) of a Book object
         and author name (string) in the order requested by the user.
    :return:
        book_data: A list with the title, author and cover url
    """
    book_data = []
    for book, author_name in books:
        book_data.append({
            "title": book.title,
            "author": author_name,
            "cover_url": book.cover_url,
            "book_id": book.id,
        })
    return book_data


@app.route('/', methods=["GET"])
def index():
    """
    renders the home.html with the books data title, author and cover.
    It gets the cover-url through the google books API
    Note: Sometimes it is very slow and also the request sometimes fails.
    Please try again in that case.

    The user can sort how the books are displayed by title and author. By
    default the books are displayed ordered by title.
    """
    success_delete = request.args.get("success_delete")
    search = request.args.get("search", "")
    sort = request.args.get("sort", "title")
    stmt = (
        db.select(Book, Author.name)
        .outerjoin(Author)
    )
    if search:
        stmt = stmt.where(
            db.or_(
                Book.title.ilike(f"%{search}%"),
                Author.name.ilike(f"%{search}%")
            )
        )
    if sort == "author":
        books = db.session.execute(
            stmt.order_by(Author.name)
        ).all()
    else:
        books = db.session.execute(
            stmt.order_by(Book.title)
        ).all()
    if books:
        book_data = get_books_data(books)
        return render_template("home.html", books=book_data, success_delete=success_delete), 200
    no_success = f"No books match this search criteria: {search}"
    return render_template("home.html", success_delete=success_delete, no_success=no_success), 200


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
    return render_template("add_author.html"), 200


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
        author_id = request.form.get("author_id")
        if author_id == "":
            author_id = None
        isbn = request.form["isbn"].replace("-", "").replace(" ", "")
        book = Book(
            title=request.form["title"],
            isbn=isbn,
            publication_year=publication_year,
            cover_url=get_cover_url(isbn),
            author_id=author_id
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
    return render_template("add_book.html", authors=authors), 200


@app.route('/book/<int:book_id>/delete', methods=["POST"])
def delete_book(book_id):
    """Deletes a book by its ID.

        Searches in the database for a book matching the provided ID.
        If found, the book is removed from the database, and the user is
        redirected to the homepage and a successful message is displayed.

        Args:
            book_id (int): The id of the book to delete.

        Returns:
            It the book with the given id exists, the book entry is deleted
            from the database.
            Redirects to the home page with a success or
            error message in the query parameters.
        """

    book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar_one_or_none()
    author_to_delete = db.session.execute(db.select(Author).where(Author.id == book_to_delete.author_id)).scalar_one_or_none()
    if book_to_delete:
        db.session.delete(book_to_delete)
        db.session.commit()
        remaining_books = db.session.execute(
            db.select(Book).where(Book.author_id == book_to_delete.author_id)
        ).scalars().first()
        if remaining_books is None:
            db.session.delete(author_to_delete)
            db.session.commit()
            return redirect(url_for('index', success_delete=f"The book {book_to_delete.title} and the author {author_to_delete.name} have been deleted successfully."))
        return redirect(url_for('index', success_delete=f"The book {book_to_delete.title} has been deleted successfully."))
    return redirect(url_for('index', success_delete=f"The book with the id {book_id} was not found."))


@app.route("/book/<int:book_id>", methods=["GET"])
def book_details(book_id):
    """Renders a book details page with all the information
     that is included in the database of the book and the author.

    Searches in the database for a book matching the provided ID and
     its author.
    If found, the details page is rendered, if not an error message is
    displayed.
    Args:
        book_id (int): The id of the book to delete.

    Returns:
        It the book with the given id exists, the book entry is deleted
        from the database.
        Redirects to the home page with a success or
        error message in the query parameters.
    """
    result = db.session.execute(
        db.select(Book, Author).outerjoin(Author).where(Book.id == book_id)
    ).one_or_none()
    if result is None:
        return f"The book with id {book_id} was not found", 400
    book, author = result
    return render_template("book_details.html", book=book, author=author)


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
