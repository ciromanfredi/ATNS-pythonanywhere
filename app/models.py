# app/models.py

#
from app import db
# hash password
from flask_bcrypt import Bcrypt
# per il token
import jwt
from datetime import datetime, timedelta

from flask import current_app

from flask_security import RoleMixin, UserMixin, SQLAlchemyUserDatastore
from flask_security.utils import verify_password
from flask_security.registerable import register_user

from sqlalchemy import *

partecipa = db.Table('partecipa',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True)
)

roles_users_table = db.Table('roles_users',
  db.Column('users_id', db.Integer(), 
  db.ForeignKey('users.id')),
  db.Column('roles_id', db.Integer(), 
  db.ForeignKey('roles.id')))

class Roles(db.Model, RoleMixin):
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(80), unique=True)
  description = db.Column(db.String(255))

class User(UserMixin,db.Model):
    """This class defines the users table """

    __tablename__ = 'users'

    # Define the columns of the users table, starting with the primary key
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(256), nullable=False)
    cognome = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    username = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    citta = db.Column(db.String(256))
    telefono = db.Column(db.String(256))
    url_image = db.Column(db.String(256))

    eventi_partecipo = db.relationship("Event",
                secondary=partecipa,
                back_populates="partecipanti")

    event_proprietario = db.relationship("Event")

    roles = db.relationship('Roles',
                secondary=roles_users_table,
                backref='user', lazy=True)
        
    #email, password,username,nome,cognome,citta,telefono,active,roles
    def __init__(self,**kwargs):
        """Initialize the user with an email and a password."""
        print('Inizializzo User')
        print(kwargs)
        self.email = kwargs['email']
        self.password = kwargs['password']
        self.active=kwargs['active']
        self.roles=kwargs['roles']

        self.username=kwargs['username']
        self.nome=kwargs['nome']
        self.cognome=kwargs['cognome']
        
        if 'citta' in kwargs:
            self.citta=kwargs['citta']
        if 'telefono' in kwargs:
            self.telefono=kwargs['telefono']
        if 'url_image' in kwargs:
            self.url_image=kwargs['url_image']

    def save(self):
        db.session.add(self)
        db.session.commit()

    #funziona
    def password_is_valid(self, password):
        """
        Checks the password against it's hash to validates the user's password
        """
        return verify_password(password, self.password) 

    #funziona
    def __repr__(self):
        """Return a representation of a user instance."""
        return "<User: {} {} {} {} {} {} {}>".format(self.email,self.password,self.username,self.nome,self.cognome,self.telefono,self.citta)

class Event(db.Model):
    """This class defines the events table."""

    __tablename__ = 'events'

    # define the columns of the table, starting with its primary key
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    date =  db.Column(db.DateTime,nullable=False)
    numbersplayer = db.Column(db.Integer,nullable=False)
    price = db.Column(db.Float,nullable=False)
    sport = db.Column(db.String(255),nullable=False)
    latitudine = db.Column(db.String(255))
    longitudine = db.Column(db.String(255))
    id_proprietario = db.Column(db.Integer, db.ForeignKey('users.id'))
    partecipanti =  db.relationship("User",
                secondary=partecipa,
                back_populates="eventi_partecipo")

    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, name, date, numbersplayer, price, sport, id_proprietario, latitudine, longitudine):
        """Initialize the event."""
        self.name = name
        self.date = date
        self.numbersplayer = numbersplayer
        self.price = price
        self.sport = sport
        self.id_proprietario = id_proprietario
        if latitudine:
            self.latitudine=latitudine
        if longitudine:
            self.longitudine=longitudine

    def save(self):
        """Save a event.
        This applies for both creating a new event
        and updating an existing onupdate
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all(user_id):
        """This method gets all the bucketlists for a given user."""
        return Bucketlist.query.filter_by(created_by=user_id)

    def delete(self):
        """Deletes a given bucketlist."""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """Return a representation of a event instance."""
        return "<Event: {}>".format(self.name)

user_datastore = SQLAlchemyUserDatastore(db, User, Roles)