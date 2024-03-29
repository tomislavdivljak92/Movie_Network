from datetime import datetime
from movie_wl import db, login_manager
from flask import current_app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer


# Define the association table for the watchlist
watchlist = db.Table(
    'watchlist',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)



followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey('user.id')),
    db.Column("followed_id", db.Integer, db.ForeignKey('user.id'))
    )



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
    followed = db.relationship("User", secondary=followers, primaryjoin=(followers.c.follower_id == id), secondaryjoin=(followers.c.followed_id ==id),
    backref = db.backref("followers", lazy="dynamic"),lazy="dynamic")
    # Define the watchlist relationship
    watchlist = db.relationship("Post", secondary=watchlist,
                                backref=db.backref('watchlist_users', lazy=True))

    def add_to_watchlist(self, post):
        try:
            if post not in self.watchlist:
                self.watchlist.append(post)
                db.session.add(self)  # Add the user instance to the session
                db.session.commit()  # Commit the changes to the database 
        except Exception as e:
            db.session.rollback()  # Rollback changes if an error occurs
            print(f"An error occurred while adding movie to watchlist: {e}")


    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id)
        return followed.union(self.posts).order_by(Post.date_posted.desc())

    def get_reset_token(self, expires_sec=900):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='reset_token')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='reset_token', max_age=900)['user_id']
        except:
            return None
        return User.query.get(user_id)



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
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User')

    def __repr__(self):
        return f"PostMain('{self.user.username}', '{self.date_posted}')"
    
    

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post_main.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    post = db.relationship('PostMain', backref=db.backref('likes', cascade='all, delete-orphan'))
    user = db.relationship('User')

    def __repr__(self):
        return f"Like('{self.post_id}', '{self.user_id}')"






class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id])




class UploadMusic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    uploader_username = db.Column(db.String(64), nullable=False)
    file_path = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return f"<MusicFile {self.filename}>"