from flask import Blueprint, render_template, redirect, session, request, url_for, flash, abort, current_app, jsonify
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from datetime import datetime
import time
from flask_wtf.csrf import generate_csrf
from time import localtime, strftime
from movie_wl import db, bcrypt, mail, socketio, ROOMS
from movie_wl.models import Post, User, PostMain, Messages, Like
from movie_wl.forms import MovieForm, RegistrationForm, LoginForm, EditDetails, PostForm, EditProfileForm, EditPost, ResetPasswordForm, RequestResetForm, ChangeEmailForm,ChangePasswordForm
import secrets
from PIL import Image
import os
from flask_mail import Message
from flask_socketio import send, emit, SocketIO, join_room, leave_room


pages = Blueprint("pages", __name__, template_folder="templates", static_folder="static")

@pages.route('/')
def main():
    if current_user.is_authenticated:
        page = request.args.get("page", 1, type=int)
        form = PostForm()
       

        followed_user_ids = [user.id for user in current_user.followed]
        followed_user_ids.append(current_user.id)
        
        # Query top-rated movies from the current user and the users they follow
        top_movies = Post.query.filter(Post.user_id.in_(followed_user_ids)).order_by(Post.rate.desc()).limit(10).all()
        

        posts = PostMain.query.filter(PostMain.user_id.in_(followed_user_ids)).order_by(PostMain.date_posted.desc()).paginate(page=page, per_page=5)

        post_likes = {}  # Dictionary to store likes for each post
        for post in posts.items:
            post_likes[post.id] = Like.query.filter_by(post_id=post.id).count()

        members = User.query.filter(User.id != current_user.id).order_by(User.username.desc()).all()
        csrf_token = generate_csrf()  # Generate CSRF token
        return render_template("main.html", title="MS Network", form=form, posts=posts, members = members, top_movies=top_movies, csrf_token=csrf_token, post_likes=post_likes)
    
    # If user is not authenticated, redirect to login
    return redirect(url_for(".login"))

@pages.route('/', methods=['POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        # Store content and username in the database
        post = PostMain(user_id=current_user.id, content=form.content.data)
        db.session.add(post)
        db.session.commit()
        
    return redirect(url_for(".main"))
    
    


    



@pages.route("/watchlist", methods=["GET", "POST"])
@login_required
def watchlist():
    sort_option = request.args.get("sort_option", "Date")  # Default sorting option is "Date"
    page = request.args.get("page", 1, type=int)
    if sort_option == "Year":
        movie_data = Post.query.filter_by(user_id=current_user.id).order_by(Post.year.desc()).paginate(page=page, per_page=5)
    elif sort_option == "Rate":
        movie_data = Post.query.filter_by(user_id=current_user.id).order_by(Post.rate.desc()).paginate(page=page, per_page=5)
    elif sort_option == "Alphabetical":  # Handle alphabetical sorting
        movie_data = Post.query.filter_by(user_id=current_user.id).order_by(Post.title).paginate(page=page, per_page=5)
    else:
        # Default sorting by date_posted
        movie_data = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)

    return render_template("watchlist.html", title="Movies Watchlist", movie_data=movie_data, sort_option=sort_option)


@pages.route("/search")
def search():
    if current_user.is_authenticated:
        q = request.args.get("q")
        if q: 
                results = Post.query.filter(
                (Post.user_id == current_user.id) &  \
                (Post.title.icontains(q) | Post.director.icontains(q)) \
            ).order_by(Post.date_posted.desc()).limit(5).all()
        else:
            results = []

        return render_template("search.html", results=results)

        
@pages.route("/edit_post/<int:post_id>/edit_post", methods=["GET","POST"])
@login_required
def edit_post(post_id):
    form = EditPost()
    post = PostMain.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.content = form.content.data

        db.session.commit()

        return redirect(url_for(".main"))
    
    elif request.method == 'GET':
        form.content.data = post.content
    
    return render_template("edit_post.html", title="Edit Post", form=form)

@pages.route("/account/edit_post/<int:post_id>/edit_post", methods=["GET","POST"])
@login_required
def edit_post_acc(post_id):
    form = EditPost()
    post = PostMain.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.content = form.content.data

        db.session.commit()

        return redirect(url_for(".account"))
    
    elif request.method == 'GET':
        form.content.data = post.content
    
    return render_template("edit_post.html", title="Edit Post", form=form)
               


@pages.route("/add", methods=["GET", "POST"])
@login_required
def add_movie():
    form = MovieForm()

    if form.validate_on_submit():
        post = Post(title=form.title.data, director=form.director.data, year=form.year.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for(".watchlist"))
    return render_template("new_movie.html", title="Add Movie", form=form)


@pages.get("/movie/<int:post_id>")
@login_required
def movie(post_id):
    movie_data = Post.query.get_or_404(post_id)
    return render_template("movie_details.html", title="Movie Details", movie_data=movie_data)

@pages.get("/movie/<int:post_id>/rate")
@login_required
def rate_movie(post_id):
    rate = int(request.args.get("rate"))
    # Update the rate for the specified movie in the database
    post = Post.query.filter_by(id=post_id).first()
    if post:
        post.rate = rate
        db.session.commit()
    
    return redirect(url_for(".movie", post_id=post_id))

@pages.route("/movie/<int:post_id>/watch", methods=["GET","POST"])
@login_required
def watch_today(post_id):
    post = Post.query.get_or_404(post_id)

    post.last_watched = datetime.now()
    db.session.commit()


    return redirect(url_for(".movie", post_id=post_id))

@pages.route("/edit_movie/<int:post_id>/edit_movie", methods=["GET","POST"])
@login_required
def edit_movie(post_id):
    post = Post.query.get_or_404(post_id)
    form = EditDetails()

    if form.validate_on_submit():
        # Update existing post data
        post.title = form.title.data
        post.director = form.director.data
        post.year = form.year.data
        #Add additional data
        post.genre = form.genre.data
        post.video_link = form.video_link.data
        post.description = form.description.data
        post.main_cast = form.main_cast.data

        db.session.commit()
        
        return redirect(url_for(".movie", post_id=post_id))
    
    elif request.method == 'GET':
        # Prefill the form with existing post data
        form.title.data = post.title
        form.director.data = post.director
        form.year.data = post.year
        form.genre.data = post.genre
        form.video_link.data = post.video_link
        form.description.data = post.description
        form.main_cast.data = post.main_cast
    return render_template('movie_form.html', title='Edit Movie', form=form)

@pages.route("/movie/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_movie(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for(".watchlist", post_id=post_id))



@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    return redirect(request.args.get("current_page"))


@pages.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('.main'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('.login'))
    return render_template('register.html', title='Register', form=form)


@pages.route("/reset_password", methods=["GET","POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('.main'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("The email has been sent, including instructions to reset your pasword.", 'success')
        return redirect(url_for('.login'))
    return render_template("reset_password_request.html", title="Reset Password", form=form)


@pages.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('.main'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)







def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender="tomislavdivljak92@gmail.com", recipients=[user.email])
    
    msg.body = f'''To reset your password, visit the following link:
{url_for('pages.reset_token', token=token, _external=True)}

If you did not make this request, ignore it.'''
    
    mail.send(msg)





@pages.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('.main'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@pages.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('.main'))


@pages.route("/account", methods=["GET", "POST"])
@login_required
def account():
    
    if current_user.image_file:
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    else:
        image_file = url_for('static', filename='static\profile_pics\default.png')

    user_posts = PostMain.query.filter_by(user_id=current_user.id).order_by(PostMain.date_posted.desc()).all()
    
    return render_template('account.html', title='Account', image_file=image_file, user_posts=user_posts)



@pages.route("/user_profile/<username>", methods=["GET", "POST"])
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('.main'))

    user_posts = PostMain.query.filter_by(user_id=user.id).order_by(PostMain.date_posted.desc()).all()
    
    return render_template('user_profile.html', title='User Profile', user=user, user_posts=user_posts)




def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_txt = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_txt
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn



@pages.route("/edit_profile", methods=["GET","POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        
        return redirect(url_for(".account"))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("edit_profile.html", title="Edit Profile", image_file=image_file, form=form)

@pages.route("/about")
def about():
    return render_template("about.html")


@pages.route("/members")
@login_required
def members():

    members = User.query.filter(User.id != current_user.id).order_by(User.username.desc()).all()
    return render_template("members.html", members = members)


@pages.route("/top_rated_movies")
@login_required
def top_rated_movies():

     # Get the IDs of the current user and the users they follow
    followed_user_ids = [user.id for user in current_user.followed]
    followed_user_ids.append(current_user.id)

    # Query top-rated movies from the current user and the users they follow
    top_movies = Post.query.filter(Post.user_id.in_(followed_user_ids)).order_by(Post.rate.desc()).limit(10).all()
    
    return render_template("top_rated_movies.html", top_movies = top_movies)



@pages.route("/post<int:post_id>/delete_post", methods=["POST"])
@login_required
def delete_post(post_id):
    post = PostMain.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for(".main"))



@pages.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        
        return redirect(url_for("pages.main"))

    if user == current_user:
        
        return redirect(url_for("pages.account", username=username))

    current_user.follow(user)
    db.session.commit()

    redirect_url = request.form.get('redirect_url')
    if redirect_url:
        return redirect(redirect_url)
    else:
        return redirect(request.referrer)

@pages.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        
        return redirect(url_for("pages.main"))

    if user == current_user:
        
        return redirect(url_for("pages.account", username=username))

    current_user.unfollow(user)
    db.session.commit()

    redirect_url = request.form.get('redirect_url')
    if redirect_url:
        return redirect(redirect_url)
    else:
        return redirect(request.referrer)

@pages.route("/followers/<username>")
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    followers = user.followers.all()
    return render_template("user_list.html", title="Followers", users=followers)

@pages.route("/followings/<username>")
@login_required
def followings(username):
    user = User.query.filter_by(username=username).first_or_404()
    followings = user.followed.all()
    return render_template("user_list.html", title="Following", users=followings)







@socketio.on('message')
def message(data):

    
    print(f"/n/n{data}/n/n")
    send({'msg': data['msg'], 'username': data['username'], 'time_stamp': 
        strftime('%b-%d %I:%M%p', localtime())}, room=data['room'])




@pages.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    # Fetch all unique users the current user has chatted with
    chatted_users = db.session.query(Messages.recipient_id).filter(Messages.sender_id == current_user.id).distinct().all()
    chatted_users_extend = db.session.query(Messages.sender_id).filter(Messages.recipient_id == current_user.id).distinct().all()

    # Extract sender and recipient IDs
    chatted_users_sender_ids = [user[0] for user in chatted_users]
    chatted_users_recipient_ids = [user[0] for user in chatted_users_extend]

    # Combine sender and recipient IDs and remove duplicates
    chatted_users_ids = list(set(chatted_users_sender_ids + chatted_users_recipient_ids))

    # Fetch usernames of the chatted users
    chatted_usernames = [user.username for user in User.query.filter(User.id.in_(chatted_users_ids)).all()]
    
    # Fetch followed users
    followed_users = current_user.followed.all()

    return render_template("chat.html", username=current_user.username, chatted_usernames=chatted_usernames, followed_users=followed_users, rooms=ROOMS)



@socketio.on("join")
def join(data):

    join_room(data['room'])

    send({'msg': data['username'] + " has joined the " + data['room'] + " room."}, room=data['room'])



@socketio.on('leave')
def leave(data):

    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + data['room'] + " room."}, room=data['room'])







@pages.route("/direct_message")
@login_required
def direct_message():
    followed_users = current_user.followed.all()
    return render_template("direct_message.html", followed_users=followed_users)

@pages.route("/send_direct_message", methods=["POST"])
@login_required
def send_direct_message():
    recipient_id = request.form.get("recipient_id")
    message_content = request.form.get("message")

    if recipient_id and message_content:
        new_message = Messages(sender_id=current_user.id, recipient_id=recipient_id, content=message_content, timestamp=datetime.utcnow())
        db.session.add(new_message)
        db.session.commit()
        return "Message sent successfully", 200
    else:
        return "Recipient ID or message content is empty", 400

@pages.route("/fetch_direct_messages", methods=["GET"])
@login_required
def fetch_direct_messages():
    user_id = request.args.get("user_id")
    
    # Fetch messages and join with the User table to get the sender's username
    messages = db.session.query(Messages, User.username).join(User, Messages.sender_id == User.id).filter(
        ((Messages.sender_id == current_user.id) & (Messages.recipient_id == user_id)) |
        ((Messages.sender_id == user_id) & (Messages.recipient_id == current_user.id))
    ).order_by(Messages.timestamp).all()
    
    # Prepare message data including sender's username
    message_data = [{"sender_username": sender_username, "content": message.content, "timestamp": message.timestamp} for message, sender_username in messages]
    
    return jsonify(message_data)


@pages.route("/search_users", methods=["GET"])
@login_required
def search_users():
    term = request.args.get("term")
    # Perform search for users matching the term
    users = User.query.filter(User.username.ilike(f"%{term}%")).all()
    # Prepare data in the required format for autocomplete
    users_data = [{"label": user.username, "value": user.username, "id": user.id} for user in users]
    return jsonify(users_data)


@pages.route("/fetch_chatted_users", methods=["GET"])
@login_required
def fetch_chatted_users():
    # Fetch the list of chatted users from the database
    chatted_users = current_user.chatted_users.all()
    # Prepare data in the required format
    chatted_users_data = [{"id": user.id, "username": user.username} for user in chatted_users]
    return jsonify(chatted_users_data)




@pages.route("/settings")
def settings():
    return render_template("settings.html")





@pages.route('/change_email', methods=['GET', 'POST'])
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        # Handle form submission
        new_email = form.new_email.data
        password = form.password.data
        # Perform necessary actions (e.g., validation, updating database)
        # Simulate success for demonstration purposes
        flash('Email successfully changed.', 'success')
        return redirect(url_for('.settings'))
    return render_template('change_email.html', form=form)



@pages.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # Handle form submission
        current_password = form.current_password.data
        new_password = form.new_password.data
        # Perform necessary actions (e.g., validation, updating database)
        # Simulate success for demonstration purposes
        flash('Password successfully changed.', 'success')
        return redirect(url_for('.settings'))
    return render_template('change_password.html', form=form)





@pages.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = PostMain.query.get_or_404(post_id)
    like_exists = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()

    if like_exists:
        db.session.delete(like_exists)
    else:
        like = Like(post_id=post.id, user_id=current_user.id)
        db.session.add(like)

    db.session.commit()

    likes_count = post.likes.count()
    return jsonify({'likes': likes_count})



@pages.route('/post-likes/<int:post_id>')
def post_likes(post_id):
    post = PostMain.query.get_or_404(post_id)
    likes = Like.query.filter_by(post_id=post_id).all()
    return render_template('post_likes.html', post=post, likes=likes)