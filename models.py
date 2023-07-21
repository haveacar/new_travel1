from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self,email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<Client %r>' % self.email

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    text = db.Column(db.Text, nullable=False)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow())

    def __init__(self,title, stars, name, text):
        self.title = title
        self.stars = stars
        self.name = name
        self.text = text

    def __repr__(self):
        return '<Review %r>' % self.title