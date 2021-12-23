'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import request
from flask_restplus import Namespace, Resource, fields, Api
from http import HTTPStatus
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.wrappers import Response
from node.networking.peering_functions import authenticateLocalUser, addPeer


namespace = Namespace('peer_controls', 'Peer Controls')

@namespace.route('/addPeer/<string:ip_address>/<int:port>')
class remove_blocks(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def put(self,ip_address,port):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        peer = addPeer(ip_address, port, status='unpeered')

        return {
            'auth_key': peer
        }


