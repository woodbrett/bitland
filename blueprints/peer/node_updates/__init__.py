'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import request
from flask_restplus import Namespace, Resource, fields, Api
from http import HTTPStatus
from node.networking.peering_functions import authenticate_peer
from node.networking.node_update_functions import queue_new_block_from_peer

namespace = Namespace('node_updates', 'Node Updates')

block_model = namespace.model('Blockchain', {
    'block': fields.String(
        required=True,
        description='Encoded block'
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
        block = request.json['block']
        ip_address = request.remote_addr
        
        x = queue_new_block_from_peer(block,ip_address)
        print(x)
        
        status = 'success'

        return {
            'status': status
        }


#UPDATE
#send transaction


