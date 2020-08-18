# profile/__init__.py

from flask import Blueprint

# This instance of a Blueprint that represents the authentication blueprint
profile_blueprint = Blueprint('profile', __name__)

from . import views