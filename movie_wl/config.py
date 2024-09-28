import os



class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY_MW")
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI_MW')  # Update the variable name
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ['EMAIL_USER_MN']
    MAIL_PASSWORD = os.environ['MAIL_APP_PASSWORD_MN']

    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    PROJECT_ID = os.environ.get("PROJECT_ID")
    REDIRECT_URI = os.environ.get("REDIRECT_URI")
    GOOGLE_CREDENTIALS_PATH = os.environ.get("GOOGLE_CREDENTIALS_PATH")


    UPLOAD_FOLDER = 'C:/Users/Mir/UploadMusic'