'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import request
from flask_restplus import Namespace, Resource, fields, Api
from http import HTTPStatus
from node.networking.peering_functions import authenticate_peer
from node.networking.node_update_functions import (
    queueNewBlockFromPeer,
    queueNewTransactionFromPeer
    )

namespace = Namespace('node_updates', 'Node Updates')

block_model = namespace.model('Blocks', {
    'block_height': fields.Integer(
        required=True,
        description='Block height'
    ),
    'block': fields.String(
        required=True,
        description='Encoded block'
    )
})

transaction_model = namespace.model('Transaction', {
    'transaction': fields.String(
        required=True,
        description='Encoded transaction'
    )
})


#UPDATE
@namespace.route('/sendNewBlock')
class send_new_block(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.expect(block_model)
    @namespace.doc(security='Bearer')   
    def put(self):
        
        if authenticate_peer(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated as peer')
        
        print(request.json['block'])
        block_height = request.json['block_height']
        block = request.json['block']
        ip_address = request.remote_addr
        
        x = queueNewBlockFromPeer(block_height,block,ip_address)
        print(x)
        
        status = 'received'

        return {
            'status': status
        }


#UPDATE
@namespace.route('/sendNewTransaction')
class send_new_transaction(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.expect(transaction_model)
    @namespace.doc(security='Bearer')   
    def put(self):
        
        if authenticate_peer(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated as peer')
        
        transaction = request.json['transaction']
        ip_address = request.remote_addr
        
        x = queueNewTransactionFromPeer(transaction_hex=transaction,peer=ip_address)
        print(x)
        
        status = 'received'

        return {
            'status': status
        }



