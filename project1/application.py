import os
import sys
import time
import json
import requests

from flask import Flask, render_template, request, url_for,flash,session,redirect,json,jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, desc
from books_database import *
from review_database import *
from register import *
from sqlalchemy import or_
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")



# Configure session to use filesystem
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
engine = create_engine(os.getenv("DATABASE_URL"))
Session(app)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return redirect(url_for('register'))



@app.route("/register",methods=["POST","GET"])
def register():
    if request.method == "GET":
        return render_template("Registration.html")
    elif(request.method == "POST"):
        
        username = request.form.get("uname")
        email = request.form.get("email")
        gender = request.form.get("gender")
        password =  generate_password_hash(str(request.form.get("pwd")))
        cpassword = request.form.get("cpwd")

        userData = User.query.filter_by(Email=email).first()
        if userData is not None:
            return render_template("Registration.html", message="email already exists, Please login.")
        else:
            user = User(Username=username,
                        Email=email, Gender=gender,Password=password,Cpassword=cpassword, Time_registered=time.ctime(time.time()))
            db.session.add(user)
            db.session.commit()
            session["username"] = username
            return render_template("userDetails.html")
    else:

        return render_template("errorpage.html")





@app.route("/login", methods=["GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")


@app.route("/admin")
def allusers():
    user = User.query.order_by(User.Time_registered).all()
    
    return render_template("admin.html", users=user)





@app.route("/auth", methods=["POST", "GET"])
def auth():
    if request.method == "POST":
        username = request.form.get('uname')
        passwd = request.form.get('pwd')

        userData = User.query.filter_by(Username=username).first()

        if userData is not None and check_password_hash(userData.Password,passwd):
            if userData.Username == username:
                session["username"] = username
                #return render_template('search.html',username=username)
                return redirect(url_for('home',username=username))

            else:
                return render_template("Registration.html", message="username/password is incorrect!!")
        else:
            return render_template("Registration.html", message="Account doesn't exists, Please register!")
    else:
        return render_template("login.html")

@app.route("/home/<username>")
def home(username):
    try:
        if "username" in session:
            return render_template("search.html", username=username)
    except:
        usermessage = "Login to view Book Review Site"
        return render_template("login.html", logg = usermessage)


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for('/'))



@app.route("/search",methods=["POST","GET"])
def search():
    if "username" in session:
        username = session["username"]

        if request.method == "GET":
            return render_template("search.html")
        else:
            result = request.form.get("search")
            result = '%'+result+'%'
            search_result = Books.query.filter(or_(Books.tittle.ilike(result), Books.author.ilike(result), Books.isbn.ilike(result))).all()
            if len(search_result) == 0:
                return render_template("search.html",message = "No records found")
            return render_template("search.html", books=search_result)
    else:
        return redirect(url_for("register"))

@app.route("/bookpage/<isbn>", methods = ["POST","GET"])
def bookpage(isbn):
    
    book_isbn=isbn

    if "username" in session:
            username = session["username"]
            user_reviews = reviewRate.query.filter_by(Isbn = book_isbn).all()
            search_result = Books.query.filter_by(isbn=book_isbn).first()
            res = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "fKvLN1nI7uY5XcyXi7VgvQ", "isbns": book_isbn})
            data = res.text
            parsed = json.loads(data)
            print(parsed)

            res = {}
            for i in parsed:
                for j in (parsed[i]):
                    res = j

            if request.method == "GET":
                revie = reviewRate.query.filter(reviewRate.Isbn.like(book_isbn),reviewRate.Username.like(username)).first()

                

                if revie is None:
                    return render_template("bookpage.html",book=search_result,res=res,review = user_reviews,username = username)
                return render_template("bookpage.html",book=search_result,message="You already given review!",review = user_reviews,res=res,property="none",username=username)

            else:
                rating = request.form.get("rating")
                reviews = request.form.get("review")

                isbn = book_isbn
                username = username
                
                user = reviewRate(Isbn=book_isbn,Review = reviews, Rating=rating,Username = username)
                db.session.add(user)
                db.session.commit()
                user_reviews = reviewRate.query.filter_by(Isbn = book_isbn).all()
                return render_template("bookpage.html",res=res,book=search_result,review=user_reviews,property="none",message="You reviewed this book")
    else:
            return redirect(url_for("/"))


@app.route("/api/search/", methods=["POST"])
def api_search():
    if request.method == "POST":
        jsobj = request.json

        result = jsobj["search"]
        result = '%' + result + '%'
        search_result = Books.query.filter(or_(Books.tittle.ilike(result), Books.author.ilike(result), Books.isbn.ilike(result),Books.year.ilike(result))).all()
        
        if search_result is None:
            return jsonify({"error": "No results found"}), 400

        book_isbn = []
        book_title = []
        book_author = []
        book_year = []


        for book in search_result:
            book_isbn.append(book.isbn)
            book_title.append(book.tittle)
            book_author.append(book.author)
            book_year.append(book.year)

        book_dict = {
        "isbn": book_isbn,
        "title": book_title,
        "author": book_author,
        "year": book_year
        }

        print(book_dict)

        return jsonify(book_dict), 200
        
    
    return jsonify({"error" : "Server Error"}), 500




@app.route("/api/book/", methods=["POST"])
def book_api():

    if request.method == "POST":
        var = request.json
        res = var["isbn"]
        username=var["username"]
        isbn = res
        username = username

        book = Books.query.filter_by(isbn=isbn).first()
        print(book)
        res = requests.get(
            "https://www.goodreads.com/book/review_counts.json",
            params={"key": "fKvLN1nI7uY5XcyXi7VgvQ", "isbns": isbn},
        )

        # Parsing the data
        data = res.text
        parsed = json.loads(data)
        print(parsed)
        res = {}
        for i in parsed:
            for j in parsed[i]:
                res = j

        dbreviews = reviewRate.query.filter_by(isbn=isbn).all()
        rew = []
        time = []
        usr = []
        for rev in dbreviews:
            rew.append(rev.review)
            time.append(rev.time_stamp)
            usr.append(rev.username)

        if book is None:
            return jsonify({"error": "Book not found"}), 400

        dict = {
            "isbn": book.isbn,
            "title": book.tittle,
            "author": book.author,
            "year": book.year,
            "average_rating": res["average_rating"],
            "average_reviewcount": res["reviews_count"],
            "review": rew,
            "time_stamp": time,
            "username": usr
        }
        return jsonify(dict), 200


@app.route("/api/review/", methods=["POST"])
def review_api():
    if request.method == "POST":

        obj = request.json
        isbn = obj["isbn"]
        user1 = obj["username"]
        rating = obj["rating"]
        reviews = obj["reviews"]

        rev_From_db = reviewRate.query.filter(reviewRate.isbn.like(isbn), reviewRate.username.like(user1)
        ).first()

        # if the user doesnt give the review for that book
        if rev_From_db is None:

            try:
                # bring the book details
                book = Books.query.filter_by(isbn=isbn).first()
                
            except:
                message = "Enter valid ISBN"
                return jsonify(message), 404

            timestamp = time.ctime(time.time())
            user = reviewRate(
                isbn=isbn,
                username=user1,
                review=reviews,
                rating=rating,
                time_stamp=timestamp)
            db.session.add(user)
            db.session.commit()

            dbreviews = reviewRate.query.filter_by(isbn=isbn).all()
            rew = []
            timeStamp = []
            usr = []
            for rev in dbreviews:
                rew.append(rev.review)
                timeStamp.append(rev.time_stamp)
                usr.append(rev.username)

            dict = {
                "isbn": isbn,
                "review": rew,
                "time_stamp": timeStamp,
                "username": usr,
                "message": "You reviewed this book.",
            }

            return jsonify(dict), 200
            print(dict)
        else:
            dict = {"message": "You already reviewed this book."}
            return jsonify(dict), 200
            print(dict)
          