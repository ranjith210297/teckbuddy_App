
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	__tablename__ = "users"
	Username = db.Column(db.String, unique=True,primary_key=True)
	Email = db.Column(db.String, unique=True, nullable=False)
	Gender = db.Column(db.String,nullable=False)
	Password = db.Column(db.String, nullable=False)
	Cpassword = db.Column(db.String, nullable=False)
	Time_registered = db.Column(db.DateTime, nullable=False)
	


