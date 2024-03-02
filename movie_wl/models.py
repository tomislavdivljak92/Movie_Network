from datetime import datetime
from movie_wl import db, login_manager
from flask import current_app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.png")
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship("Post", backref="author", lazy=True)

    def __repr__(self):
        return f"User ('{self.username}', '{self.email}', '{self.image_file}')"
    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    director = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Integer, default=0)
    main_cast = db.Column(db.String(50), nullable=True)
    genre = db.Column(db.String(50), nullable=True)
    last_watched = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.String(500), nullable=True)
    video_link = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"    
    


class PostMain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    comments = db.Column(db.Text, nullable=True)
    likes = db.Column(db.Integer, nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User')

    def __repr__(self):
        return f"PostMain('{self.user.username}', '{self.date_posted}')"
