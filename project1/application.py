import os
import sys
import time

from flask import Flask, render_template, request, url_for,flash,session,redirect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, desc
from register import *
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime


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
	if 'Username' in session:
		return redirect(url_for('home'))
	return redirect(url_for('register'))


@app.route("/register")
def register():
	return render_template("registration.html")


@app.route("/login")
def login():
	return render_template("login.html")


@app.route("/admin")
def allusers():
    user = User.query.order_by(User.Time_registered).all()
    for i in user:
    	print(i.Username,i.Password,i.Time_registered)

    return render_template("admin.html", users=user)


@app.route("/userDetails", methods=["POST", "GET"])
def userDetails():
	db.create_all()
	if request.method == "POST":
		username = request.form.get("uname")
		email = request.form.get("email")
		gender = request.form.get("gender")
		password = request.form.get("pwd")
		cpassword = request.form.get("cpwd")
		userData = User.query.filter_by(Email=email).first()
		if userData is not None:
			return render_template("registration.html", message="email already exists, Please login.")
		else:
			user = User(Username=username,
                        Email=email, Gender=gender,Password=password,Cpassword=cpassword, Time_registered=time.ctime(time.time()))
			db.session.add(user)
			db.session.commit()
			session[username] = request.form['uname']
			return render_template("userDetails.html")
	return render_template("errorpage.html")



@app.route("/auth", methods=["POST", "GET"])
def auth():
    if request.method == "POST":
        username = request.form.get('uname')
        passwd = request.form.get('pwd')

        userData = User.query.filter_by(Username=username).first()

        if userData is not None:
            if userData.Username == username and userData.Password == passwd:
                session[username] = username
                return render_template('userHome.html', user=username)
            else:
                return render_template("registration.html", message="username/password is incorrect!!")
        else:
            return render_template("registration.html", message="Account doesn't exists, Please register!")
    else:
        return "<h1>Please login/register instead.</h1>"



@app.route("/logout")
def logout():
    session.pop('Username', None)
    return redirect(url_for('index'))


@app.route("/home/<Username>")
def userHome(Username):
    if Username in session:
        return render_template("userDetails.html", username=Username, message="Successfully logged in.", heading="Welcome back")
    return redirect(url_for('index'))
