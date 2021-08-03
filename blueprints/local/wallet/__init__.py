'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import request
from flask_restplus import Namespace, Resource, fields, Api
from http import HTTPStatus
from wallet.broadcast_transaction import broadcastTransaction
from node.networking.peering_functions import authenticateLocalUser

namespace = Namespace('wallet', 'Wallet')

transaction_model = namespace.model('Blocks', {
    'transaction': fields.String(
        required=True,
        description='Serialized transaction'
    )
})

#only available to local user
@namespace.route('/broadcastTransaction')
class broadcast_transaction(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.expect(transaction_model)
    @namespace.doc(security='Bearer')   
    def put(self):
        
        print(request.remote_addr)
        print(request.headers.get("Authorization"))
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        print("validated")
        
        transaction = request.json['transaction']
        
        x = broadcastTransaction(transaction)
        print(x)
        
        status = 'received'

        return {
            'status': status
        }





