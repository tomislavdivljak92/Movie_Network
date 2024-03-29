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


    UPLOAD_FOLDER = 'C:/Users/Mir/UploadMusic'