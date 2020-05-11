import os
import sys
import time
import json


from flask import Flask, render_template, request, url_for,flash,session,redirect, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, desc
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
	if 'username' in session:
		return redirect(url_for('home'))
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
			session[username] = request.form['uname']
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
            if userData.Username == username :
                session[username] = username
                return render_template('search.html')
            else:
                return render_template("Registration.html", message="username/password is incorrect!!")
        else:
            return render_template("Registration.html", message="Account doesn't exists, Please register!")
    else:
        return render_template("login.html")



@app.route("/logout")
def logout():
    session.pop('Username', None)
    return redirect(url_for('index'))


@app.route("/home")
def userHome():
	if "username" in session:
		username = session["username"]
		return render_template("userDetails.html", username=username, message="Successfully logged in.", heading="Welcome back")
	return redirect(url_for('index'))


@app.route("/bookpage/<isbn>", methods = ["POST","GET"])
def bookpage(isbn):
	
	book_isbn=isbn

	if "username" in session:
			username = session["username"]
			user_reviews = reviewRate.query.filter_by(Isbn = book_isbn).all()
			res = request.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "fKvLN1nI7uY5XcyXi7VgvQ", "isbns": book_isbn})
			if request.method == "GET":
				revie = reviewRate.query.filter(reviewRate.Isbn.like(book_isbn),reviewRate.Username.like(username)).first()

				search_result = books.query.filter_by(isbn=book_isbn).all()

				if revie is None:
					return render_template("bookpage.html",book=search_result,res=res,review = user_reviews,username = username)
				return render_template("bookpage.html",book=search_result,message="You already given review!",review = user_reviews,res=res,property="none",username=username)

			else:
				print("no")
				rating = request.form.get("rating")
				reviews = request.form.get("Review")

				isbn = book_isbn
				username = username

				user = reviewRate(Isbn=book_isbn,Review = reviews, Rating=rating,Username = username)
				db.session.add(user)
				db.session.commit()

				return render_template("bookpage.html",res=res,book=search_result,review=user_reviews,property="none",message="You reviewed this book")
	else:
			return redirect(url_for("/"))

@app.route('/books/<id>', methods=['POST','GET'])
def books(id):
    try:
        user = session["email"]
        result = db.session.query(books).filter(books.isbn == id).first()
        data=reviewRate.query.all()
        r=reviewRate.query.filter_by(isbn=id).all()
        if request.method =='POST':
            reviewdata = reviewRate(id,user,request.form['comment'], request.form['rating'])
            user = reviewRate.query.filter_by(email = user, isbn = id).first()
            data = reviewRate.query.all()
            if user is not None:
                print("user has already given rating")
                var1 = "Error : User has already given rating"
                return render_template("Book_page.html",user = user, Book_details = result,var1=var1, comments=r, allreviewdata = data)
                db.session.add(reviewdata)
                db.session.commit()
                var1 = "Review Submitted"
                flash(var1)
                return redirect(url_for('books',id=id))
            
            else:
                return render_template("Book_page.html",user = user, Book_details = result, comments=r, allreviewdata = data)
    
    except Exception as e:
        print(e)
        var1 = "You must login to view the homepage"
        return render_template("reg.html", var1=var1)

@app.route('/api/submitReview', methods=['POST'])
def submitreview():
    if not request.is_json:
        message="Invalid request format"
        return jsonify(message),400
    isbn = request.args.get('isbn')
    try:
        result = db.session.query(books).filter(books.isbn == isbn).first()
    except:
        message="please try again later"
        return jsonify(message),500
    if result is None:
        message="please enter valid isbn"
        return jsonify(message),404
    rating = request.get_json()['rating']
    comment=request.get_json()['comment']
    email = request.get_json()['email']
    user = reviewRate.query.filter_by(email=email, isbn=isbn).first()
    if user is not None:
        message = "Sorry, you cannot review this book again"
        return jsonify(message),409
    reviewdata=reviewRate(isbn=isbn,email=email,comment=comment,rating=rating)
    try:
        db.session.add(reviewdata)
        db.session.commit()
    except:
        message="please try again"
        return jsonify(message),500
    message = "Review Submitted successfully"
    return jsonify(message),200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

