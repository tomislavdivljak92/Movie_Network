import os



class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY_MW")
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI_MW')  # Update the variable name
    SQLALCHEMY_TRACK_MODIFICATIONS = False
 