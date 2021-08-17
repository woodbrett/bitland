'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import request
from flask_restplus import Namespace, Resource, fields, Api
from http import HTTPStatus
from node.networking.peering_functions import authenticate_peer
from node.networking.node_query_functions import (
    getBlockHeightPeer,
    getBlocksStartEnd,
    getBlockByHeight
    )
import json

namespace = Namespace('node_queries', 'Node Queries')

block_height_model = namespace.model('Block Height', {
    'block_height': fields.Integer(
        required=True,
        description='Block height'
    ),
    'block_hash': fields.String(
        required=True,
        description='Block hash'
    )
})

blocks_model = namespace.model('Blocks', {
    'start_block_height': fields.String(
        required=True,
        description='Start block height'
    ),
    'blocks': fields.String(
        required=True,
        description='Blocks',
        as_list=True
    )
})

block_model = namespace.model('Block', {
    'block': fields.String(
        required=True,
        description='Block'
    )
})


@namespace.route('/getBlockHeight')
class get_block_height(Resource):
    '''Get block height of node'''

    @namespace.response(500, 'Internal Server error')
    @namespace.marshal_with(block_height_model)
    @namespace.doc(security='Bearer')   
    def get(self):
        
        if authenticate_peer(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(401, 'Not authenticated as peer')
        
        block_height = getBlockHeightPeer().get('id')
        block_hash = getBlockHeightPeer().get('header_hash')

        return {
            'block_height': block_height,
            'block_hash': block_hash
        }


@namespace.route('/getBlocks/<int:start_block>/<int:end_block>')
class get_blocks(Resource):
    '''Get blocks from starting to ending'''

    @namespace.response(500, 'Internal Server error')
    @namespace.marshal_list_with(blocks_model)
    @namespace.doc(security='Bearer')   
    def get(self, start_block, end_block):
        
        if authenticate_peer(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated as peer')
        
        blocks = getBlocksStartEnd(start_block, end_block)
        print(blocks[1])
        
        return {
            'start_block_height': blocks[0],
            'blocks': json.dumps(blocks[1])
        }


@namespace.route('/getBlock/<int:block_height>')
class get_block(Resource):
    '''Get blocks from starting to ending'''

    @namespace.response(500, 'Internal Server error')
    @namespace.marshal_with(block_model)
    @namespace.doc(security='Bearer')   
    def get(self, block_height):
        
        if authenticate_peer(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated as peer')
        
        block = getBlockByHeight(block_height)

        return {
            'blocks': block
        }

        
#UPDATE
#get_transactions

