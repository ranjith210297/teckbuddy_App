
import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,DateTime,exists,Sequence
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#app1.app_context().push()

db.init_app(app)


#class in which we create table colums for databse of books.
class Books(db.Model):
    __tablename__ = "books"
    isbn = db.Column(db.String, nullable = False,primary_key=True)
    tittle = db.Column(db.String, nullable = False)
    author = db.Column(db.String, nullable = False)
    year = db.Column(db.String, nullable= False)



#main method to import books.
def main():
    #db.create_all()
    f= open("books.csv")
    reader = csv.reader(f)
    for isbn, tittle, author, year in reader:
        book = Books(isbn= isbn, tittle=tittle, author=author, year=year)
        db.session.add(book)
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        main()
