from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///demo101.db'
db = SQLAlchemy(app)


@app.route("/")
def home():
    return "Hello World"









if __name__ == "__main__":
    with app.app_context():
         db.create_all()
    app.run(debug=True)

