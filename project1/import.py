
import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,DateTime,exists,Sequence
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy



app1 = Flask(__name__)

app1.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app1.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app1.app_context().push()

db1 = SQLAlchemy()

#class in which we create table colums for databse of books.
class Books(db1.Model):
    __tablename__ = "books"
    isbn = db1.Column(db1.String, nullable = False,primary_key=True)
    tittle = db1.Column(db1.String, nullable = False)
    author = db1.Column(db1.String, nullable = False)
    year = db1.Column(db1.String, nullable= False)

db1.init_app(app1)
db1.create_all()

#main method to import books.
def main():
    f= open("books.csv")
    reader = csv.reader(f)
    for isbn, tittle, author, year in reader:
        book = Books(isbn= isbn, tittle=tittle, author=author, year=year)
        db1.session.add(book)
    db1.session.commit()

if __name__ == "__main__":
        main()
