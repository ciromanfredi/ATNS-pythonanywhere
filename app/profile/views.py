# /app/auth/views.py

from . import profile_blueprint

from app.models import Event,partecipa,User


from flask import make_response, request, jsonify
from flask.views import MethodView

from flask_login import current_user

from flask_security.decorators import auth_required    

class ProfileView(MethodView):
    @auth_required('token')
    def get(self):
        try:
            obj = {
                        'id': current_user.id,
                        'nome': current_user.nome,
                        'cognome': current_user.cognome,
                        'username': current_user.username,
                        'citta': current_user.citta,
                        'telefono': current_user.telefono,
                        'email': current_user.email,
                        'url_image': current_user.url_image
                    }
            return make_response(jsonify(obj)), 200
        except Exception as e:
            # An error occured, therefore return a string message containing the error
            response = {
                'message': str(e)
            }
            return make_response(jsonify(response)), 401
    
    @auth_required('token')
    def put(self):
        try:
            current_user.citta = request.json.get('citta', current_user.citta)
            current_user.telefono = request.json.get('telefono', current_user.telefono)
            current_user.url_image = request.json.get('url_image',current_user.url_image)
            current_user.save()
            response = {
                'message': "Profilo modificato con successo."
            }
            return make_response(jsonify(response)), 201
        except Exception as e:
            # An error occured, therefore return a string message containing the error
            response = {
                'message': str(e)
            }
            return make_response(jsonify(response)), 401
    
@profile_blueprint.route('/profile/<int:id>',methods=['GET'])
def visitaProfilo(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            obj = {
                        'id': user.id,
                        'nome': user.nome,
                        'cognome': user.cognome,
                        'username': user.username,
                        'citta': user.citta,
                        'telefono': user.telefono,
                        'email': user.email,
                        'url_image': user.url_image
                        }
            return make_response(jsonify(obj)), 200
        else:
            # An error occured, therefore return a string message containing the error
            response = {
                'message': 'Non esiste alcun utente con tale id.'
            }
            return make_response(jsonify(response)), 201 
    except Exception as e:
        # An error occured, therefore return a string message containing the error
        response = {
            'message': str(e)
        }
        return make_response(jsonify(response)), 401

# Define the API resource
profile_view = ProfileView.as_view('profile_view')

# Define the rule for the registration url --->  /auth/register
# Then add the rule to the blueprint
profile_blueprint.add_url_rule(
    '/profile',
    view_func=profile_view,
    methods=['GET','PUT'])
