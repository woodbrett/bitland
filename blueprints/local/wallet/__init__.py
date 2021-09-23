'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import request
from flask_restplus import Namespace, Resource, fields, Api
from http import HTTPStatus
from wallet.broadcast_transaction import broadcastTransaction
from node.networking.peering_functions import authenticateLocalUser
from wallet.key_generation import generateRandomKeys, savePublicPrivateKeysDb
from wallet.information import getWalletUtxos

namespace = Namespace('wallet', 'Wallet')

@namespace.route('/generatePublicPrivateKey/<string:save_keys_to_db>')
@namespace.doc(params={'save_keys_to_db': 'this should be a value of "True" or "False"'})
class generate_public_private_key(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self, save_keys_to_db):

        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        key_pair = generateRandomKeys()
        key_pair.update({'saved_to_db':False})
        
        if save_keys_to_db.lower() == "true":
            savePublicPrivateKeysDb(key_pair.get('private_key'),key_pair.get('public_key'))
            key_pair.update({'saved_to_db':True})
        
        return key_pair


@namespace.route('/utxos')
class utxos(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self):

        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        utxos = getWalletUtxos()
        
        return utxos




