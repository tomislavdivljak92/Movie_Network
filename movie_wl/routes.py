from flask import Blueprint, render_template, redirect, session, request, url_for, flash, abort, current_app, jsonify, send_file
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from datetime import datetime
from werkzeug.utils import secure_filename
from movie_wl.config import Config
from movie_wl.imdb_utils import get_top_10_movies, get_bottom_10_movies
from flask_wtf.csrf import generate_csrf
from time import localtime, strftime
from movie_wl import db, bcrypt, mail, socketio, ROOMS
from movie_wl.models import Post, User, PostMain, Messages, Like, UploadMusic
from movie_wl.forms import MovieForm, RegistrationForm, LoginForm, EditDetails, PostForm, EditProfileForm, EditPost, ResetPasswordForm, RequestResetForm, ChangeEmailForm,ChangePasswordForm, UploadMusicForm
import secrets
from PIL import Image
import os
import pathlib
from sqlalchemy import func, or_
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from movie_wl.drive_utils import upload_to_drive, get_drive_service
from google.oauth2 import service_account
import requests
import io
from movie_wl.google_login_utils import initiate_google_login, handle_google_callback

from flask_mail import Message
from flask_socketio import send, emit, SocketIO, join_room, leave_room


                                    
pages = Blueprint("pages", __name__, template_folder="templates", static_folder="static")

@pages.route('/')
def main():
    if current_user.is_authenticated:
        page = request.args.get("page", 1, type=int)
        sort_option = request.args.get("sort_option", "Newest")  # Default sorting option is "Date"
        form = PostForm()
        
        followed_user_ids = [user.id for user in current_user.followed]
        followed_user_ids.append(current_user.id)
        
        # Query top-rated movies from the current user and the users they follow
        top_movies = Post.query.filter(Post.user_id.in_(followed_user_ids)).order_by(Post.rate.desc()).limit(10).all()
        
        # Determine the sorting method based on the selected option
        if sort_option == "Oldest":
            posts = PostMain.query.filter(PostMain.user_id.in_(followed_user_ids)).order_by(PostMain.date_posted.asc()).paginate(page=page, per_page=5)
        elif sort_option == "Most Liked":
            # Join the Like table and count the number of likes for each post
            posts = PostMain.query \
                .outerjoin(Like, PostMain.id == Like.post_id) \
                .filter(PostMain.user_id.in_(followed_user_ids)) \
                .group_by(PostMain.id) \
                .order_by(func.count(Like.id).desc()) \
                .paginate(page=page, per_page=5)
        else:
            posts = PostMain.query.filter(PostMain.user_id.in_(followed_user_ids)).order_by(PostMain.date_posted.desc()).paginate(page=page, per_page=5)

        post_likes = {}  # Dictionary to store likes for each post
        for post in posts.items:
            post_likes[post.id] = Like.query.filter_by(post_id=post.id).count()

        # Fetch top and bottom 10 movies using IMDbPY
        imdb_top_10 = get_top_10_movies()
        imdb_bottom_10 = get_bottom_10_movies()
        members = User.query.filter(User.id != current_user.id).order_by(User.username.desc()).limit(10).all()
        csrf_token = generate_csrf()  # Generate CSRF token
        return render_template("main.html", title="MS Network", form=form, posts=posts, members=members, top_movies=top_movies, csrf_token=csrf_token, post_likes=post_likes, sort_option=sort_option,
            imdb_top_10=imdb_top_10,
            imdb_bottom_10=imdb_bottom_10)
    
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

    # Fetch all movies posted by the user
    user_movies = Post.query.filter_by(user_id=current_user.id)

    # Fetch all movie IDs from the watchlist
    watchlist_movie_ids = [movie.id for movie in current_user.watchlist]

    # Query all movies from the watchlist based on their IDs
    watchlist_movies = Post.query.filter(Post.id.in_(watchlist_movie_ids))
    

    # Combine both lists
    all_movies = user_movies.union(watchlist_movies)
    

    # Apply sorting based on the selected option directly in the database query
    if sort_option == "Year":
        all_movies = all_movies.order_by(Post.year.desc())
    elif sort_option == "Rate":
        all_movies = all_movies.order_by(Post.rate.desc())
    elif sort_option == "Alphabetical":
        all_movies = all_movies.order_by(Post.title)
    else:
        all_movies = all_movies.order_by(Post.date_posted.desc())

    # Paginate the sorted list
    movie_data = all_movies.paginate(page=page, per_page=5)
    print(movie)

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
    try:
        movie_data = Post.query.get_or_404(post_id)
        return render_template("movie_details.html", title="Movie Details", movie_data=movie_data)
    except Exception as e:
        
        abort(500)

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

@pages.route("/movie/<int:post_id>/watch", methods=["GET", "POST"])
@login_required
def watch_today(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        post.last_watched = datetime.now()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while updating the watch time.", "error")
        return redirect(url_for("pages.error"))
    
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
    # Attempt to get the movie from the Post database
    post = Post.query.get_or_404(post_id)
    
    # Check if the movie with the specified post_id exists in the current user's watchlist
    watchlist_movie = None
    for movie in current_user.watchlist:
        if movie.id == post_id:
            watchlist_movie = movie
            break
    
    # If the current user is not the author of the movie, remove it from their watchlist only
    if post.author != current_user:
        if watchlist_movie:
            current_user.watchlist.remove(watchlist_movie)
            db.session.commit()  # Commit the removal from the watchlist
    else:
        # If the current user is the author of the movie, delete it entirely from the database
        db.session.delete(post)
        db.session.commit()
    
    return redirect(url_for(".watchlist"))



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
        
        db.session.commit()
        
        return redirect(url_for(".account"))
    elif request.method == 'GET':
        form.username.data = current_user.username
        
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("edit_profile.html", title="Edit Profile", image_file=image_file, form=form)

@pages.route("/about")
def about():
    try:
        return render_template("about.html")
    except Exception:
        return "<h1>Something went wrong. Please try again later.</h1>", 500


@pages.route("/members")
@login_required
def members():
    try:
        members = User.query.filter(User.id != current_user.id).order_by(User.username.desc()).all()
        return render_template("members.html", members=members)
    except Exception as e:
        # Log the exception or handle it as needed
        print(f"An error occurred: {e}")
        flash("An error occurred while fetching members. Please try again later.", "error")
        return redirect(url_for("pages.main"))

@pages.route("/top_rated_movies")
@login_required
def top_rated_movies():
    try:
        # Get the IDs of the current user and the users they follow
        followed_user_ids = [user.id for user in current_user.followed]
        followed_user_ids.append(current_user.id)

        # Query top-rated movies from the current user and the users they follow
        top_movies = Post.query.filter(Post.user_id.in_(followed_user_ids)).order_by(Post.rate.desc()).limit(10).all()
        
        return render_template("top_rated_movies.html", top_movies=top_movies)
    
    except Exception as e:
        # Handle exceptions by aborting with a 500 error code
        abort(500)



@pages.route("/add_to_watchlist/<int:post_id>", methods=["POST"])
@login_required
def add_to_watchlist(post_id):
    try:
        post = Post.query.get_or_404(post_id)
        current_user.add_to_watchlist(post)  # Invoke the add_to_watchlist method
        flash('Movie has been added to your watchlist!', 'success')
    except Exception as e:
        flash('An error occurred while adding the movie to your watchlist.', 'danger')
    return redirect(url_for('.top_rated_movies'))


@pages.route("/post<int:post_id>/delete_post", methods=["POST"])
@login_required
def delete_post(post_id):
    try:
        post = PostMain.query.get_or_404(post_id)
        
        # Check if the current user is the owner of the post
        if post.user_id != current_user.id:
            abort(403)
        Like.query.filter_by(post_id=post_id).delete()

        db.session.delete(post)
        db.session.commit()
        
        return redirect(url_for(".main"))

    except Exception as e:
        # Rollback the session in case of any errors
        db.session.rollback()     
        flash("An error occurred while deleting the post. Please try again later.", "error")
 
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

from flask import flash, redirect, url_for

@pages.route("/followers/<username>")
@login_required
def followers(username):
    try:
        user = User.query.filter_by(username=username).first_or_404()
        followers = user.followers.all()
        return render_template("user_list.html", title="Followers", users=followers)
    except Exception as e:
        flash("An unexpected error occurred. Please try again later.", "danger")
        return redirect(url_for(".main")) 

@pages.route("/followings/<username>")
@login_required
def followings(username):
    try:
        user = User.query.filter_by(username=username).first_or_404()
        followings = user.followed.all()
        return render_template("user_list.html", title="Following", users=followings)
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for(".main"))




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
    
    return render_template("direct_message.html")

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



@pages.route("/delete_chat/<int:user_id>", methods=["GET", "POST"])
@login_required
def delete_chat(user_id):
    if user_id:
        # Delete chat history with the specified user
        Messages.query.filter((Messages.sender_id == current_user.id) & (Messages.recipient_id == user_id)).delete()
        Messages.query.filter((Messages.sender_id == user_id) & (Messages.recipient_id == current_user.id)).delete()
        db.session.commit()
        return "Chatted history deleted successfully", 200
    else:
        return "User ID is empty", 400



@pages.route('/start_conversation/<int:user_id>', methods=['POST'])
@login_required
def start_conversation(user_id):
    # Check if a conversation already exists with the user
    conversation = Messages.query.filter(
        ((Messages.sender_id == current_user.id) & (Messages.recipient_id == user_id)) |
        ((Messages.sender_id == user_id) & (Messages.recipient_id == current_user.id))
    ).first()

    if conversation:
        # Conversation already exists, redirect to direct_message page with conversation_id
        return redirect(url_for('.direct_message', conversation_id=conversation.id))
    else:
        # Create a new conversation
        new_conversation = Messages(sender_id=current_user.id, recipient_id=user_id, content="", timestamp=datetime.utcnow())
        db.session.add(new_conversation)
        db.session.commit()
        # Redirect to direct_message page with the newly created conversation_id
        return redirect(url_for('.direct_message', conversation_id=new_conversation.id))



@pages.route("/settings")
def settings():
    try:
        return render_template("settings.html")
    except Exception as e:
        # Log the error if necessary, then return a generic error message.
        print(f"Error loading settings page: {e}")
        return "An error occurred while loading the settings page.", 500





@pages.route('/change_email', methods=['GET', 'POST'])
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        # Handle form submission
        new_email = form.new_email.data
        password = form.password.data
        
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







@pages.route('/store')
def store():
    # Query the database to retrieve the list of uploaded music files
    music_files = UploadMusic.query.all()
#    print(music_files)  # Debugging line
    return render_template('store.html', music_files=music_files)

@pages.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_page():
    form = UploadMusicForm()  

    if form.validate_on_submit():
        title = form.title.data
        music_file = form.file.data  
        uploader_username = current_user.username

        try:
            
            drive_file_id = upload_to_drive(music_file)  
            
            # Create a new UploadMusic instance
            new_music = UploadMusic(
                music_title=title,  
                filename=music_file.filename,
                uploader_username=uploader_username,
                drive_file_id=drive_file_id 
            )

            
            db.session.add(new_music)
            db.session.commit()

            flash('Music uploaded successfully!', 'success')
            return redirect(url_for('pages.store'))  # Redirect to the store page after upload

        except Exception as e:
            print(f"Error occurred: {e}")
            flash(f'An error occurred: {e}', 'error')
            return redirect(request.url)  # Redirect back to the upload page if an error occurs

    return render_template('upload.html', form=form)  

@pages.route('/download/<int:id>')
@login_required 
def download_file(id):
    music_file = UploadMusic.query.get_or_404(id)
    drive_file_id = music_file.drive_file_id

    # Create the direct download link from Google Drive
    shareable_link = f'https://drive.google.com/uc?id={drive_file_id}&export=download'

    # Redirect the user to the download link
    return redirect(shareable_link)

@pages.route('/uploads/<int:id>')
def serve_file(id):
    
    music_file = UploadMusic.query.get_or_404(id)
    drive_file_id = music_file.drive_file_id

    # Generate a shareable link to the Google Drive file
    shareable_link = f'https://drive.google.com/uc?id={drive_file_id}'

    # Redirect to the Google Drive link
    return redirect(shareable_link)

@pages.route('/delete_file/<int:id>', methods=['POST'])
def delete_file(id):
    music_file = UploadMusic.query.get_or_404(id)  # Retrieve the music file or return 404 if not found

    # Check if the logged-in user is the uploader
    if music_file and music_file.uploader_username == current_user.username:  
        drive_service = get_drive_service()
        drive_service.files().delete(fileId=music_file.drive_file_id).execute()  # Delete from Google Drive
        db.session.delete(music_file)  
        db.session.commit()  
        flash('File deleted successfully!', 'success')  
    else:
        flash('You do not have permission to delete this file.', 'error')  

    return redirect(url_for('pages.store'))  

@pages.route('/audio/<drive_file_id>')
def audio(drive_file_id):
    file_url = f"https://drive.google.com/uc?export=download&id={drive_file_id}"
    response = requests.get(file_url)
    # Save the file temporarily, or stream directly
    return send_file(io.BytesIO(response.content), mimetype='audio/mpeg')



@pages.route("/login/google")
def google_login():
    """Initiates the Google login process."""
    return initiate_google_login()  # Call the utility function to start Google login

@pages.route("/google/callback")
def google_callback():
    """Handles the Google callback after user authentication."""
    user_info = handle_google_callback()  # Call the utility function to process user info

    if user_info:
        # Check if user already exists in the database
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            # Create a new user if they don't exist
            user = User(username=user_info['name'], email=user_info['email'])
            db.session.add(user)
            db.session.commit()

        # Log the user in
        login_user(user)  # Use Flask-Login to log the user in
        return redirect(url_for('.main'))  # Redirect to the main page after login

    return redirect(url_for('.login'))  # Redirect to login if user info is not available



