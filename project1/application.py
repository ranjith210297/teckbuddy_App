import os
import sys
import time

from flask import Flask, render_template, request, url_for,flash,session
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


@app.route("/")
def reroute():
	return render_template("registration.html")


@app.route("/register", methods=["POST","GET"])
def register():
	if request.method == "GET":
		return render_template("registration.html")
	elif(request.method == "POST"):
		username = request.form.get("uname")
		email = request.form.get("email")
		gender = request.form.get("gender")
		password = request.form.get("pwd")
		cpassword = request.form.get("cpwd")
		
		return render_template("userDetails.html",Username=username,Email=email,Gender=gender)



		
		
