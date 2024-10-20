from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, URLField, FileField
from wtforms.validators import InputRequired, NumberRange, DataRequired, Email, EqualTo, Length, URL
from movie_wl.models import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed

class MovieForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    director = StringField("Director", validators=[InputRequired()])


    year = IntegerField("Year", validators=[InputRequired(), NumberRange(min=1870, message="Enter a year in the format YYYY")])
    submit = SubmitField("Add Movie")


class RegistrationForm(FlaskForm):
    username = StringField("Username",
                            validators = [DataRequired(), Length(min=2, max=20)])
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_user(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username taken. Please try again.")


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email taken. Please try again.")


class LoginForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")    

class EditDetails(MovieForm):
    genre = StringField("Genre", validators=[Length(max=50)])
    main_cast = StringField("Main Cast")
    video_link = URLField("Video Link", validators=[URL()])
    description = TextAreaField("Description")
    submit = SubmitField("Submit")


class PostForm(FlaskForm):
     
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Post")

class EditPost(PostForm):
    content = TextAreaField("Edit Post", validators=[DataRequired()])
    submit = SubmitField("Update Post")










class EditProfileForm(FlaskForm):
    username = StringField("Username",
                            validators = [DataRequired(), Length(min=2, max=20)])
    
    picture = FileField("Update Profile Picture", validators=[FileAllowed(['jpg','png'])])
    
    submit = SubmitField("Update")

    def validate_user(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("Username taken. Please try again.")


    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("Email taken. Please try again.")





class RequestResetForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")
    
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with current email.")      


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                                     validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset Password")





class SendMessageForm(FlaskForm):
    recipient = StringField("Recipient Username", validators=[DataRequired()])
    content = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send")




class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Submit')


class ChangeEmailForm(FlaskForm):
    new_email = StringField('New Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UploadMusicForm(FlaskForm):
    title = StringField("Song Title", validators=[DataRequired()])
    file = FileField("Choose Music File", validators=[DataRequired(), FileAllowed(['mp3', 'wav'], 'Music files only!')])
    submit = SubmitField("Upload Music")