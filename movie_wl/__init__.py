from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from movie_wl.config import Config
from flask_mail import Mail
from flask_migrate import Migrate
from flask_socketio import SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix
# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
bcrypt = Bcrypt()
login_manager = LoginManager()
socketio = SocketIO()
ROOMS = ["NEWS", "MOVIES", "GAMES", "MUSIC"]

login_manager.login_view = 'pages.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    # Apply ProxyFix to handle the proxy and HTTPS correctly on Render
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.config['PREFERRED_URL_SCHEME'] = 'https'  # Enforce HTTPS

    # Initialize Flask extensions with the Flask application instance
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)

    from movie_wl.routes import pages
    app.register_blueprint(pages)

    return app