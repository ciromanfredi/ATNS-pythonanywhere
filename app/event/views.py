# /app/auth/views.py

from . import event_blueprint

from flask.views import MethodView
from flask import make_response, request, jsonify
from app.models import Event,partecipa,User

from flask_login import current_user
from flask_mail import Message
from app import mail
from flask_security.decorators import auth_required
from datetime import datetime

today = datetime.today()

class SingleEventView(MethodView):
    def get(self,id):
        try:
            event = Event.query.filter_by(id=id).first()
            if event:
                partecipanti = User.query.filter(User.eventi_partecipo.any(id=event.id)).all()
                id_partecipanti=[]
                #print(partecipanti)
                for partecipante in partecipanti:
                    id_partecipanti.append(partecipante.id)

                obj = {
                        'id': event.id,
                        'name': event.name,
                        'date': event.date,
                        'numbersplayer': event.numbersplayer,
                        'price': event.price,
                        'sport': event.sport,
                        'id_partecipanti': id_partecipanti,
                        'id_proprietario': event.id_proprietario,
                        'latitudine': event.latitudine,
                        'longitudine': event.longitudine                        
                        }

                return make_response(jsonify(obj)), 200
            else:
                obj = {
                            'message': 'Nessun evento con questo id'
                        }

                return make_response(jsonify(obj)), 201
        except Exception as e:
            # An error occured, therefore return a string message containing the error
            response = {
                'message': str(e)
            }
            return make_response(jsonify(response)), 401
    
    @auth_required('token')
    def delete(self,id):
        try:
            event = Event.query.filter_by(id=id).first()
            if event.id_proprietario == current_user.id:
                event.delete()
                response = {
                    'message': 'Evento cancellato con successo.'
                }
                return make_response(jsonify(response)), 201
            else:
                response = {
                    'message': 'Evento non cancellato. Non sei il proprietario.'
                }
                return make_response(jsonify(response)), 202
        except Exception as e:
            # An error occured, therefore return a string message containing the error
            response = {
                'message': str(e)
            }
            return make_response(jsonify(response)), 401
    
    @auth_required('token')
    def put(self,id):
        try:
            event = Event.query.filter_by(id=id).first()
            partecipanti = User.query.filter(User.eventi_partecipo.any(id=event.id)).all()
            id_partecipanti=[]
            #print(partecipanti)
            for partecipante in partecipanti:
                id_partecipanti.append(partecipante.id)

            print(event)
            if event:
                if current_user.id == event.id_proprietario:
                    event.name = request.json.get('name', event.name)
                    event.date = request.json.get('date', event.date)
                    event.numbersplayer = request.json.get('numbersplayer', event.numbersplayer)
                    event.price = request.json.get('price', event.price)
                    event.sport = request.json.get('sport', event.sport)
                    event.save()
                    response = {
                        'message': "Evento modificato con successo."
                    }
                    return make_response(jsonify(response)), 201
                else:
                    response = {
                        'message': "Non sei il proprietario dell'evento."
                    }
                    return make_response(jsonify(response)), 203
            else:
                response = {
                    'message': "L'evento non esiste."
                }
                return make_response(jsonify(response)), 204
        except Exception as e:
            # An error occured, therefore return a string message containing the error
            response = {
                'message': str(e)
            }
            return make_response(jsonify(response)), 401

class EventView(MethodView):

    def get(self):
        try:
            events = Event.query.filter(Event.date >= today).all()
            results = []

            for event in events:
                partecipanti = User.query.filter(User.eventi_partecipo.any(id=event.id)).all()
                id_partecipanti=[]
                #print(partecipanti)
                for partecipante in partecipanti:
                    id_partecipanti.append(partecipante.id)
                obj = {
                        'id': event.id,
                        'name': event.name,
                        'date': event.date,
                        'numbersplayer': event.numbersplayer,
                        'price': event.price,
                        'sport': event.sport,
                        'id_partecipanti': id_partecipanti,
                        'id_proprietario': event.id_proprietario,
                        'latitudine': event.latitudine,
                        'longitudine': event.longitudine                        
                        }
                results.append(obj)

            return make_response(jsonify(results)), 200
        except Exception as e:
            # An error occured, therefore return a string message containing the error
            response = {
                'message': str(e)
            }
            return make_response(jsonify(response)), 401
    
    @auth_required('token')
    def post(self):
        """Handle POST request for this view. Url ---> /event"""
        print('heeey')
        # There is no user so we'll try to register them
        try:
            post_data = request.json
            print(post_data)

            # Register the event
            name = post_data['name']
            date = post_data['date']
            numbersplayer = post_data['numbersplayer']
            price = post_data['price']
            sport = post_data['sport']
            if 'latitudine' in post_data:
                latitudine=post_data['latitudine']
            if 'longitudine' in post_data:
                longitudine=post_data['longitudine']

            if 'latitudine' in post_data and 'longitudine' in post_data:
                event = Event(name=name, date=date,numbersplayer=numbersplayer,price=price,sport=sport,id_proprietario=current_user.id,latitudine=latitudine,longitudine=longitudine)
            else:
                event = Event(name=name, date=date,numbersplayer=numbersplayer,price=price,sport=sport,id_proprietario=current_user.id,latitudine=None,longitudine=None)
            event.save()

            response = {
                'message': 'Evento creato con successo.'
            }
            # return a response notifying the user that they registered successfully
            return make_response(jsonify(response)), 201
        except Exception as e:
            # An error occured, therefore return a string message containing the error
            print('nooo')
            response = {
                'message': str(e)
            }
            return make_response(jsonify(response)), 400

@event_blueprint.route('/partecipa/<int:id>',methods=['GET'])
@auth_required('token')
def partecipa_event(id):
    try:
        event = Event.query.filter_by(id=id).first()
        if event:
            if User.query.filter(User.eventi_partecipo.any(id=event.id)).count() < event.numbersplayer:
                #print(current_user)
                current_user.eventi_partecipo.append(event)
                current_user.save()
                response = {
                    'message': 'Partecipi a questo evento con successo.'
                }
                # return a response notifying the user that they registered successfully
                return make_response(jsonify(response)), 200
            else:
                response = {
                    'message': 'Non ci sono posti disponibili per tale evento.'
                }
                # return a response notifying the user that they registered successfully
                return make_response(jsonify(response)), 201    
        else:
            response = {
                'message': 'Non esiste alcun evento con tale id.'
            }
            # return a response notifying the user that they registered successfully
            return make_response(jsonify(response)), 202
    except Exception as e:
        # An error occured, therefore return a string message containing the error
        response = {
            'message': str(e)
        }
        return make_response(jsonify(response)), 401

@event_blueprint.route('/dispartecipa/<int:id>',methods=['GET'])
@auth_required('token')
def dispartecipa(id):
    try:
        event = Event.query.filter_by(id=id).filter(Event.partecipanti.any(id=current_user.id)).first()
        #print(event)
        if event:
            event.partecipanti.remove(current_user)
            event.save()
            response = {
               'message': 'Non partecipi a questo evento con successo.'
            }
            # return a response notifying the user that they registered successfully
            return make_response(jsonify(response)), 200
        else:
            response = {
                'message': 'Non esiste alcun evento con tale id o non sei il proprietario.'
            }
            # return a response notifying the user that they registered successfully
            return make_response(jsonify(response)), 202
    except Exception as e:
        # An error occured, therefore return a string message containing the error
        response = {
            'message': str(e)
        }
        return make_response(jsonify(response)), 401

@event_blueprint.route('/invioemail',methods=['GET'])
def invioemail():
    try:
        msg = Message("Object",body='Messaggio...',
                sender="cir.manfredi@studenti.unina.it",
                recipients=["ciromanfredi96@gmail.com"])
        mail.send(msg)
        response = {
            'message': 'Email inviata con successo.'
        }
        # return a response notifying the user that they registered successfully
        return make_response(jsonify(response)), 202
    except Exception as e:
        # An error occured, therefore return a string message containing the error
        response = {
            'message': str(e)
        }
        return make_response(jsonify(response)), 401

# Define the API resource
event_view = EventView.as_view('event_view')
single_event_view = SingleEventView.as_view('single_event_view')

# Define the rule for the registration url --->  /auth/register
# Then add the rule to the blueprint
event_blueprint.add_url_rule(
    '/events',
    view_func=event_view,
    methods=['GET','POST'])

# Define the rule for the registration url --->  /auth/register
# Then add the rule to the blueprint
event_blueprint.add_url_rule(
    '/event/<id>',
    view_func=single_event_view,
    methods=['GET','DELETE','PUT'])
