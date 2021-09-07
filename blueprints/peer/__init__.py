'''
Created on Mar 28, 2021

@author: brett_wood
'''
#https://aaronluna.dev/series/flask-api-tutorial/part-3/

from flask import Blueprint
from flask_restplus import Api
from blueprints.peer.peering import namespace as peering_ns
from blueprints.peer.node_queries import namespace as node_queries_ns
from blueprints.peer.node_updates import namespace as node_updates_ns

blueprint = Blueprint('peer', __name__, url_prefix='/peer')

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

api_extension.add_namespace(peering_ns)
api_extension.add_namespace(node_queries_ns)
api_extension.add_namespace(node_updates_ns)