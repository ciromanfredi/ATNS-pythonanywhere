# app/__init__.py

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local import
from instance.config import app_config

#
from flask import request, jsonify, abort, make_response,current_app, g
from flask.sessions import SecureCookieSessionInterface
#
from flask_login import LoginManager, user_loaded_from_header
from flask_mail import Mail
from flask_security import Security, SQLAlchemyUserDatastore

from flask_cors import CORS, cross_origin

# initialize sql-alchemy
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
security = Security()

from app.models import user_datastore

@user_loaded_from_header.connect
def user_loaded_from_header(self, user=None):
    g.login_via_header = True

class CustomSessionInterface(SecureCookieSessionInterface):
    """Disable default cookie generation."""
    def should_set_cookie(self, *args, **kwargs):
        #print('app - init - CustomSessionInterface - should_set_cookie')
        return False

    """Prevent creating session from API requests."""
    def save_session(self, *args, **kwargs):
        if g.get('login_via_header'):
            print("Custom session login via header")
            return
        return super(CustomSessionInterface, self).save_session(*args,
                                                                **kwargs)

def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    #print('config_name: ',config_name)
    #print(app_config[config_name])
    #print(app.config)

    # For email
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = '12fallisco34@gmail.com'
    app.config['MAIL_PASSWORD'] = '56Fallisco'
    #app.config['MAIL_DEFAULT_SENDER'] =
    mail.init_app(app)

    # For security
    app.config['SECURITY_RECOVERABLE'] = True
    app.config['SECURITY_CONFIRMABLE'] = True
    app.config['SECURITY_CHANGEABLE'] = True
    app.config['SECURITY_REGISTERABLE'] = True
    app.config['SECURITY_PASSWORD_SALT'] = 'some arbitrary super secret string'
    app.config['SECURITY_EMAIL_SENDER'] = '12fallisco34@gmail.com'

    app.config['WTF_CSRF_ENABLED'] = False

    app.config['CORS_HEADERS'] = 'Content-Type'

    app.session_interface = CustomSessionInterface()

    db.init_app(app)
    login_manager.init_app(app)
    security.init_app(app, user_datastore)
    cors = CORS(app)

        
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        print('app - init - load_user')
        return User.query.get(int(user_id))

    
    # import the authentication blueprint and register it on the app

    from .event import event_blueprint
    app.register_blueprint(event_blueprint)

    from .profile import profile_blueprint
    app.register_blueprint(profile_blueprint)

    return app

