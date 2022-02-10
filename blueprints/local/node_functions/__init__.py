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
from node.blockchain.block_adding_queueing import removeBlocksQueueing
from node.blockchain.global_variables import bitland_version
from utilities.time_utils import getTimeNowSeconds
from utilities.bitcoin.bitcoin_requests import getBestBlockHash,\
    getBlockHeightFromHash
from node.blockchain.header_operations import calculateMerkleRoot64BitcoinBlocks,\
    getPrevBlockGuarded
from binascii import unhexlify, hexlify
from node.information.blocks import getMaxBlockHeight
from utilities.difficulty import getBitsCurrentBlock
from ecdsa.util import bit_length

namespace = Namespace('node_functions', 'Node Functions')

@namespace.route('/removeBlocks/<int:start_block>/<int:end_block>')
class remove_blocks(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def put(self,start_block,end_block):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        status = removeBlocksQueueing(start_block,end_block)

        return {
            'status': status
        }


@namespace.route('/version')
class get_current_version(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')

        return {
            'version': bitland_version
        }


@namespace.route('/time')
class get_current_time(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')

        return {
            'time': getTimeNowSeconds()
        }
        

@namespace.route('/bitcoinHash')
class get_current_bitcoin_hash(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')

        bitcoin_hash = getBestBlockHash()

        return {
            'bitcoin_hash': bitcoin_hash
        }


@namespace.route('/bitcoinHeight')
class get_current_bitcoin_height(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')

        bitcoin_hash = getBestBlockHash()
        bitcoin_height = getBlockHeightFromHash(bitcoin_hash)

        return {
            'bitcoin_height': bitcoin_height
        } 


@namespace.route('/bitcoinLast64')
class get_current_bitcoin_last_64(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')

        bitcoin_hash = getBestBlockHash()
        bitcoin_height = getBlockHeightFromHash(bitcoin_hash)
        bitcoin_last_64_mrkl_bytes = calculateMerkleRoot64BitcoinBlocks(block_height=bitcoin_height)
        
        return {
            'bitcoin_last_64_mrkl': unhexlify(bitcoin_last_64_mrkl_bytes)
        }               
        

@namespace.route('/height')
class get_current_height(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')

        current_block_height = getMaxBlockHeight()

        return {
            'height':current_block_height
        }               
        

#difficulty_bits
@namespace.route('/difficultyBits')
class get_difficulty_bits(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')

        bits_bytes = getBitsCurrentBlock()
        print(bits_bytes)
        print(hexlify(bits_bytes).decode('utf-8'))
        
        return {
            'difficulty_bits':hexlify(bits_bytes).decode('utf-8')
        }               
        

#previous block hash
@namespace.route('/previousBlockHash')
class get_previous_block_hash(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')

        previous_block_hash = getPrevBlockGuarded()
        print(previous_block_hash)

        return {
            'previous_block_hash':hexlify(previous_block_hash).decode('utf-8')
        }   

