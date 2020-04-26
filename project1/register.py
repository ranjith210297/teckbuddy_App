
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from passlib.hash import bcrypt



db = SQLAlchemy()

class User(db.Model):
	__tablename__ = "users"
	Username = db.Column(db.String, unique=True,primary_key=True)
	Email = db.Column(db.String, unique=True, nullable=False)
	Gender = db.Column(db.String,nullable=False)
	Password = db.Column(db.String, nullable=False)
	Cpassword = db.Column(db.String, nullable=False)
	Time_registered = db.Column(db.DateTime, nullable=False)

	def __init__(self,Username,Email,Gender,Password,Cpassword,Time_registered):
		self.Username=Username
		self.Email = Email
		self.Gender=Gender
		self.Password = bcrypt.encrypt(Password)
		self.Cpassword = Cpassword
		self.Time_registered = datetime.now()
	


