# **Book Alchemy**

---

Digital library using Flask and flask-sqlalchemy.

## **Description**

___

This project was developed as a practice assessment for a Software Engineering Bootcamp in Masterschool.
It demonstrates:

- dynamic web development using Jinja2 
- Flask concepts such as:
  - routing
  - template rendering
  - form handling
- Use of APIs (Google Books API)
- Object-Oriented Programming with SQL

## **Overview**

Book Alchemy creates a relational database for books, which contains two tables: 
books and author, with the corresponding information.
The content of the database is displayed through an html page.

## **Features**

___

- Display books in an html (title, author, cover)
- Delete books
- Sort books by title or author
- Search books or authors
- Display more details for each book

## Technologies Used

___

| Technology       | Purpose                                          |
|:-----------------|:-------------------------------------------------|
| Python           | Core application                                 |
| Flask            | Web framework                                    |
| flask_sqlalchemy | Extension for Flask, adds support for SQLAlchemy |
| HTML             | Generated blog website                           |
| CSS              | Style content of webpage                         |
| SQL              | Structured Query Language                        |
| Google Books API | Used to retrieve the book cover url              |


## **How It Works** ##

___

1. Run the app.py file.
2. Route /add_author: Adds author information to the database.
3. Route /add_book: Adds book information to the database.
4. Route /: Homepage: A list of books with Author and Cover is displayed
   - Search button: it searchs in title and author
   - Sort button: it sorts by title and author
   - Delete button: the user can delete the corresponding book. If the author
     of the book has no other books in the database, it will also be deleted.
     Also in the route: /book/<int:book_id>/delete
   - Link in Book title: All the information of the book and author is displayed,
     also in the route /book/<int:book_id>.

## **Installation**

___

1. Clone the repository:

```
git clone https://github.com/esterplaza/book_alchemy.git
```


5. Change git remote url to avoid accidental pushes to base project

```
   git remote set-url origin github_username/repo_name
   git remote -v # confirm the changes
```

### Required Packages

```
pip install requests flask json dotenv flask_sqlalchemy sqlalchemy.exc
```

## **Running the Application**

___

Start the program:

```
python add.py
```


## **Usage**

___


## Acknowledgments

___

- Built using Flask.
- Cover Information from Google Books API

## **Contact**

___

Ester Plaza Fernández - esterplaza@gmail.com

Project Link: https://github.com/esterplaza/book_alchemy.git
