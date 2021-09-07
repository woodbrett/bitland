'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import request
from flask_restplus import Namespace, Resource, fields
from http import HTTPStatus
from node.networking.peering_functions import evaluateConnectionRequest,\
    authenticatePeer

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

pong_model = namespace.model('Pong', {
    'message': fields.String(
        required=True,
        description='Message'
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
                
        connection_request = evaluateConnectionRequest(ip_address, version, port, timestamp)
        
        connection_status = connection_request.status
        connection_reason = connection_request.reason
        token = connection_request.token

        return {
            'status': connection_status,
            'reason': connection_reason,
            'token': token
        }

@namespace.route('/ping')
class ping(Resource):
    '''Ping peers to keep connection'''

    @namespace.response(500, 'Internal Server error')
    @namespace.marshal_with(pong_model)
    @namespace.doc(security='Bearer')   
    def get(self):
        
        if authenticatePeer(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(401, 'Not authenticated as peer')
        
        return {
            'message': 'pong'
        }


