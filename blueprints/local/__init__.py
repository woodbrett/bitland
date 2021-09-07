'''
Created on Mar 28, 2021

@author: brett_wood
'''
#https://aaronluna.dev/series/flask-api-tutorial/part-3/

from flask import Blueprint
from flask_restplus import Api
from blueprints.local.wallet import namespace as wallet_ns

blueprint = Blueprint('local', __name__, url_prefix='/local')

authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api_extension = Api(
    blueprint,
    title='Peer Endpoints',
    version='1.0',
    description='Endpoints available to network peer',
    doc='/doc',
    authorizations=authorizations
)

api_extension.add_namespace(wallet_ns)
