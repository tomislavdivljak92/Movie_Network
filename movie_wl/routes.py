from flask import Blueprint, render_template, redirect, session, request, url_for, flash, abort, current_app
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from datetime import datetime
from movie_wl import db, bcrypt
from movie_wl.models import Post, User, PostMain
from movie_wl.forms import MovieForm, RegistrationForm, LoginForm, EditDetails, PostForm, EditProfileForm
import secrets
from PIL import Image
import os

pages = Blueprint("pages", __name__, template_folder="templates", static_folder="static")




@pages.route('/')
def main():
    if current_user.is_authenticated:
        # If user is authenticated, render the main page with the form and posts
        form = PostForm()
        top_movies = Post.query.order_by(Post.rate.desc()).limit(10).all()
        posts = PostMain.query.join(User).order_by(PostMain.date_posted.desc()).all()
        members = User.query.filter(User.id != current_user.id).order_by(User.username.desc()).all()
        return render_template("main.html", title="MS Network", form=form, posts=posts, members = members, top_movies=top_movies)
    
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
    
    


    



@pages.route("/watchlist")
def watchlist():
    if current_user.is_authenticated:
        movie_data = Post.query.filter_by(user_id=current_user.id).order_by(Post.date_posted.desc()).all()
        return render_template("watchlist.html", title="Movies Watchlist", movie_data=movie_data)  
    return redirect(url_for(".login"))

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
#@pages.route("/search")
##def search():
#    if current_user.is_authenticated:
#        q = request.args.get("q")
#        print("Search term:", q)  # Debugging statement
#        if q: 
#            # Perform case-insensitive search using ilike
#           results = Post.query.filter(
#                (Post.user_id == current_user.id) &
#                (func.lower(Post.title).ilike(f"%{q.lower()}%") | func.lower(Post.director).ilike(f"%{q.lower()}%"))
#            ).order_by(Post.date_posted.desc()).limit(5).all()
#            print("Query:", results)  # Debugging statement
#        else:
#            results = []

#        return render_template("index.html", results=results)
    
    
        
        


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

    top_movies = Post.query.order_by(Post.rate.desc()).limit(10).all()
    return render_template("top_rated_movies.html", top_movies = top_movies)

