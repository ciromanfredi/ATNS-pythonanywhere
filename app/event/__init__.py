# auth/__init__.py

from flask import Blueprint

# This instance of a Blueprint that represents the authentication blueprint
event_blueprint = Blueprint('event', __name__)

from . import views