'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import request
from flask_restplus import Namespace, Resource, fields, Api
from http import HTTPStatus
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.wrappers import Response
from node.networking.peering_functions import authenticateLocalUser, addPeer,\
    attemptToConnectToNewPeer, queryPeerByIpAndPort, queryPeers
from utilities.time_utils import getTimeNowSeconds
from node.blockchain.global_variables import bitland_version
from system_variables import peering_port


namespace = Namespace('peer_controls', 'Peer Controls')

@namespace.route('/addPeer/<string:ip_address>/<int:port>')
class add_peer(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def put(self,ip_address,port):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        peer = addPeer(ip_address, port, status='unpeered')

        return {
            'auth_key': peer
        }


@namespace.route('/connectToPeer/<string:ip_address>/<int:port>')
class connect_to_peer(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self,ip_address,port):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        peer = attemptToConnectToNewPeer(bitland_version, peering_port, getTimeNowSeconds(), ip_address, port)

        return {
            'status': peer
        }


@namespace.route('/peerList')
class peer_list(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        peer_list = queryPeers()

        return peer_list


