import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class reviewRate(db.Model):
    __tablename__ = "review_rate"
    isbn = db.Column(db.String, nullable=False, primary_key=True)
    username = db.Column(db.String, nullable=False, primary_key=True)
    rating = db.Column(db.String, nullable=False)
    review = db.Column(db.String, nullable=False)
    time_stamp = db.Column(db.String, nullable=False)
    





