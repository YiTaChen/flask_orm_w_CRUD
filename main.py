from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///demo101.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(80), unique = False, nullable = False)
    email = db.Column(db.String(120), unique = False, nullable = False)
    borrowed_books = db.relationship('Borrow', backref='borrowed_user', lazy=True)
    def to_dic(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }


class Book(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    title = db.Column(db.String(80), unique = False, nullable = False)
    author_id = db.Column(db.String(120), db.ForeignKey("author.id"), nullable = False)
    borrows = db.relationship('Borrow', backref='borrowed_book', lazy=True)
    def to_dic(self):
        return {
            "id": self.id,
            "title": self.title,
            "author_id": self.author_id
        }


class Author(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(80), unique = False, nullable = False)
    books = db.relationship('Book', backref='author', lazy=True)
    def to_dic(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    user_id = db.Column(db.String(120), db.ForeignKey("user.id"), nullable = False)
    book_id = db.Column(db.String(80), db.ForeignKey("book.id"), nullable = False)
    borrow_date = db.Column(db.DateTime, nullable = False)
    def to_dic(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "borrow_date": self.borrow_date
        }



@app.route("/")
def home():
    return "Hello World"


# User CRUD:
# Create a new user
@app.route("/user", methods = ['POST'])
def create_user():
    data = request.json 
    user = User(name = data["name"], email = data["email"])
    db.session.add(user)
    db.session.commit()
    return {"message":"User created"}, 201


# Get all users
@app.route("/users", methods = ['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify(users = [ user.to_dic() for user in users ]), 200


# Get a user by ID
@app.route("/user/<id>", methods = ['GET'])
def get_user_by_id(id:int):
    user = User.query.get(id)
    return jsonify(user.to_dic()), 200


# Update user details
@app.route("/user/<id>", methods = ['PUT', 'PATCH'])
def update_user(id:int):
    user = User.query.get(id)
    if not user: 
        return {"message":"User not found"}, 404
    json_data = request.json
    user_columns = User.__table__.columns.keys()
    for update_key in json_data.keys():
        if update_key in user_columns:
            setattr(user, update_key, json_data[update_key])   
    db.session.commit()     
    return {"message":"User updated"}, 200

# Delete a user
@app.route("/user/<id>", methods = ['DELETE'])
def delete_user(id:int):
    user = User.query.get(id)
    if not user:
        return {"message":"User not found"}, 404
    db.session.delete(user)
    db.session.commit()
    return {"message":"User deleted"}, 200


# Book CRUD:
# Add a new book
@app.route("/book", methods = ['POST'])
def create_book():
    data = request.json 
    book = Book(title = data["title"], author_id = data["author_id"])
    db.session.add(book)
    db.session.commit()
    return {"message":"Book created"}, 201


# Get all books
@app.route("/books", methods = ['GET'])
def get_all_books():
    books = Book.query.all()
    return jsonify(books = [ book.to_dic() for book in books ]), 200

# Get books by author
@app.route("/books/filter", methods = ['GET'])
def get_books_by_author():
    author_id = request.args.get("author_id")
    books = Book.query.filter_by(author_id = author_id).all()
    return jsonify(books = [ book.to_dic() for book in books ]), 200

# Delete a book
@app.route("/book/<id>", methods = ['DELETE'])
def delete_book(id:int):
    book = Book.query.get(id)
    if not book:
        return {"message":"Book not found"}, 404
    db.session.delete(book)
    db.session.commit()
    return {"message":"Book deleted"}, 200


# Author CRUD:
# Add a new author
@app.route("/author", methods = ['POST'])
def create_author():
    data = request.json 
    author = Author(name = data["name"])
    db.session.add(author)
    db.session.commit()
    return {"message":"Author created"}, 201

# Get all authors
@app.route("/authors", methods = ['GET'])
def get_all_authors():
    authors = Author.query.all()
    return jsonify(authors = [ author.to_dic() for author in authors ]), 200

# Get an author’s books
@app.route("/author/<author_id>/books", methods = ['GET'])
def get_author_books(author_id):
    books = Author.query.get(author_id).books
    return jsonify(books = [ book.to_dic() for book in books ]), 200


# Borrow CRUD:
# Borrow a book (create a borrow record)
@app.route("/borrow", methods = ['POST'])   
def borrow_a_book():
    data = request.json
    datetime_str = datetime.strptime( data["borrow_date"], "%Y-%m-%d") if data.get("borrow_date") else datetime.utcnow()
    borrow = Borrow(user_id = data["user_id"], book_id = data["book_id"], borrow_date =datetime_str)
    db.session.add(borrow)
    db.session.commit()
    return {"message":"Borrow created"}, 201

@app.route("/borrows", methods = ['GET'])
def show_borrows():
    borrows = Borrow.query.all()
    return jsonify(borrows = [ borrow.to_dic() for borrow in borrows ]), 200


# Get all borrowed books for a user
@app.route("/borrow/user/<user_id>/books", methods = ['GET'])
def get_books_borrowed_by_user(user_id:int):
    borrows = Borrow.query.filter_by(user_id = user_id).all()
    books = [borrow.borrowed_book for borrow in borrows]
    return jsonify(books = [ book.to_dic() for book in books ]), 200

# Get all users who borrowed a particular book
@app.route("/borrow/book/<book_id>/users", methods = ['GET'])
def get_users_borrowed_book(book_id:int):
    book = Book.query.get(book_id)
    users = [borrow.borrowed_user for borrow in book.borrows]
    return jsonify(users = [ user.to_dic() for user in users ]), 200



if __name__ == "__main__":
    with app.app_context():
         db.create_all()
    app.run(debug=True)

