
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class USERS(db.Model):
	__tablename__ = "USERS"
	user_name = db.Column(db.String, primary_key=True)
	email = db.Column(db.String, nullable=False)
	gender = db.Column(db.String,nullable=False)
	passwd = db.Column(db.String, nullable=False)
	cpasswd = db.Column(db.String, nullable=False)
	registered_time = db.Column(db.DateTime, nullable = False)


