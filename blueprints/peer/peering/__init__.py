'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import request
from flask_restplus import Namespace, Resource, fields
from http import HTTPStatus
from node.networking.peering_functions import evaluate_connection_request

namespace = Namespace('peering', 'Peering')

request_to_connect_model = namespace.model('Request to Connect', {
    'version': fields.String(
        required=True,
        description='Version'
    ),
    'port': fields.Integer(
        required=True,
        description='Port'
    ),
    'timestamp': fields.Integer(
        required=True,
        description='Timestamp'
    )
})

connection_info_model = namespace.model('Connection Results', {
    'status': fields.String(
        required=True,
        description='Connection Status'
    ),
    'reason': fields.String(
        required=True,
        description='Connection Reason'
    ),
    'token': fields.String(
        required=True,
        description='Token'
    )
})


@namespace.route('/connect')
class connect(Resource):
    '''Attempt to connect'''

    @namespace.response(400, 'Not available to connect')
    @namespace.response(500, 'Internal Server error')
    @namespace.expect(request_to_connect_model)
    @namespace.marshal_with(connection_info_model, code=HTTPStatus.CREATED)
    def post(self):

        ip_address = request.remote_addr
        version = request.json['version']
        port = request.json['port']
        timestamp = request.json['timestamp']
                
        connection_request = evaluate_connection_request(ip_address, version, port, timestamp)
        
        connection_status = connection_request.status
        connection_reason = connection_request.reason
        token = connection_request.token

        return {
            'status': connection_status,
            'reason': connection_reason,
            'token': token
        }

#UPDATE
#ping pong




