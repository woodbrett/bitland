'''
Created on Mar 28, 2021

@author: brett_wood
'''
#https://aaronluna.dev/series/flask-api-tutorial/part-3/

from flask import Blueprint
from flask_restplus import Api
from blueprints.local.wallet import namespace as wallet_ns
from blueprints.local.blockchain_data import namespace as blockchain_data_ns
from blueprints.local.transaction import namespace as transaction_ns
from blueprints.local.node_functions import namespace as node_functions_ns
from blueprints.local.peer_controls import namespace as peer_controls_ns

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
    title='Local Endpoints',
    version='1.0',
    description='Endpoints available to local network',
    doc='/doc',
    authorizations=authorizations
)

api_extension.add_namespace(wallet_ns)
api_extension.add_namespace(blockchain_data_ns)
api_extension.add_namespace(transaction_ns)
api_extension.add_namespace(node_functions_ns)
api_extension.add_namespace(peer_controls_ns)