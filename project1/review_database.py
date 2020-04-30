from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class reviewRate(db.Model):
    _tablename_ = "reviews"
    isbn = db.Column(db.String, nullable=False, primary_key=True)
    username = db.Column(db.String, nullable=False, primary_key=True)
    rating = db.Column(db.String, nullable=False)
    review = db.Column(db.String, nullable=False)
    



app1 = Flask(_name_)

app1.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app1.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app1.app_context().push()

db1 = SQLAlchemy()

db1.init_app(app1)
db1.create_all()