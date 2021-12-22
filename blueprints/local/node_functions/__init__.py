'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import request
from flask_restplus import Namespace, Resource, fields, Api
from http import HTTPStatus
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.wrappers import Response
from node.networking.peering_functions import authenticateLocalUser
from node.blockchain.block_adding_queueing import removeBlocksThreading

namespace = Namespace('node_functions', 'Node Functions')

@namespace.route('/removeBlocks/<int:start_block>/<int:end_block>')
class remove_blocks(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def put(self,start_block,end_block):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        status = removeBlocksThreading(start_block,end_block)

        return {
            'status': status
        }

