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
from wallet.transaction_creation import createSimpleTransactionTransfer,\
    createTransactionClaim, createSimpleTransactionTransferContingencies
from binascii import hexlify

namespace = Namespace('transaction', 'Transaction')

broadcast_model = namespace.model('Broadcast Transaction', {
    'serialized_transaction': fields.String(
        required=True,
        description='Serialized transaction'
    )
})

transaction_simple_model = namespace.model('Transaction Simple', {
    'input_transaction_hash': fields.String(
        required=True,
        description='Input Transaction Hash'
    ),
    'input_vout': fields.Integer(
        required=True,
        description='Input Vout'
    ),
    'input_private_key': fields.String(
        required=True,
        description='Input Private Key'
    ),
    'input_spend_type': fields.Integer(
        required=True,
        description='Input Spend Type: 1 - standard spend (which could be a successful collateral); 2 - spending as collateral; 3 - make claim; 4 - spend failed transfer; 5 - spend successful claim'
    ),
    'output_public_key': fields.String(
        required=True,
        description='Output Public Key'
    )
})

transaction_simple_contingencies_model = namespace.model('Transaction Simple Contingencies', {
    'input_transaction_hash': fields.String(
        required=True,
        description='Input Transaction Hash'
    ),
    'input_vout': fields.Integer(
        required=True,
        description='Input Vout'
    ),
    'input_private_key': fields.String(
        required=True,
        description='Input Private Key'
    ),
    'input_spend_type': fields.Integer(
        required=True,
        description='Input Spend Type: 1 - standard spend (which could be a successful collateral); 2 - spending as collateral; 3 - make claim; 4 - spend failed transfer; 5 - spend successful claim'
    ),
    'output_public_key': fields.String(
        required=True,
        description='Output Public Key'
    ),
    'miner_fee_sats': fields.Integer(
        required=True,
        description='Miner Fee Sats'
    ),
    'miner_fee_blocks': fields.Integer(
        required=True,
        description='Miner Fee Blocks'
    ),
    'transfer_fee_sats': fields.Integer(
        required=True,
        description='Transfer Fee Sats'
    ),
    'transfer_fee_blocks': fields.Integer(
        required=True,
        description='Transfer Fee Blocks'
    ),
    'transfer_fee_address': fields.String(
        required=True,
        description='Transfer Fee Address'
    )
})

transaction_claim_model = namespace.model('Transaction Claim', {
    'input_transaction_hash': fields.String(
        required=True,
        description='Input Transaction Hash'
    ),
    'input_vout': fields.Integer(
        required=True,
        description='Input Vout'
    ),
    'miner_fee_sats': fields.Integer(
        required=True,
        description='Miner Fee Sats'
    ),
    'miner_fee_blocks': fields.Integer(
        required=True,
        description='Miner Fee Blocks'
    ),
    'output_public_key': fields.String(
        required=True,
        description='Output Public Key'
    )
})



@namespace.route('/broadcastSerializedTransaction')
class broadcast_serialized_transaction(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.expect(broadcast_model)
    @namespace.doc(security='Bearer')   
    def post(self):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        transaction = request.json['serialized_transaction']
        
        x = broadcastTransaction(transaction)

        return {
            'status': 'broadcasted successfully'
        }


@namespace.route('/createSerializedTransactionSimple')
class create_serialized_transaction_simple(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.expect(transaction_simple_model)
    @namespace.doc(security='Bearer')   
    def post(self):

        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        input_transaction_hash = request.json['input_transaction_hash']
        input_vout = request.json['input_vout']
        input_private_key = request.json['input_private_key']        
        input_spend_type = request.json['input_spend_type']
        output_public_key = request.json['output_public_key']        
        
        serialized_transaction = createSimpleTransactionTransfer(input_transaction_hash, input_vout, input_private_key, input_spend_type, output_public_key)
        serialized_transaction_hex = hexlify(serialized_transaction).decode('utf-8')
        
        return {
            'serialized_transaction': serialized_transaction_hex
        }


@namespace.route('/createSerializedTransactionSimpleContingencies')
class create_serialized_transaction_simple_contingencies(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.expect(transaction_simple_contingencies_model)
    @namespace.doc(security='Bearer')   
    def post(self):

        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        input_transaction_hash = request.json['input_transaction_hash']
        input_vout = request.json['input_vout']
        input_private_key = request.json['input_private_key']        
        input_spend_type = request.json['input_spend_type']
        output_public_key = request.json['output_public_key']     
        miner_fee_sats = request.json['miner_fee_sats']
        miner_fee_blocks = request.json['miner_fee_blocks']
        transfer_fee_sats = request.json['transfer_fee_sats']        
        transfer_fee_blocks = request.json['transfer_fee_blocks']
        transfer_fee_address = request.json['transfer_fee_address']    
        
        serialized_transaction = createSimpleTransactionTransferContingencies(input_transaction_hash, input_vout, input_private_key, input_spend_type, output_public_key,miner_fee_sats, miner_fee_blocks, transfer_fee_sats, transfer_fee_blocks, transfer_fee_address)
        serialized_transaction_hex = hexlify(serialized_transaction).decode('utf-8')
        
        return {
            'serialized_transaction': serialized_transaction_hex
        }


@namespace.route('/createSerializedTransactionClaim')
class create_serialized_transaction_claim(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.expect(transaction_claim_model)
    @namespace.doc(security='Bearer')   
    def post(self):

        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        input_transaction_hash = request.json['input_transaction_hash']
        input_vout = request.json['input_vout']
        miner_fee_sats = request.json['miner_fee_sats']        
        miner_fee_blocks = request.json['miner_fee_blocks']
        output_public_key = request.json['output_public_key']        
        
        serialized_transaction = createTransactionClaim(input_transaction_hash, input_vout, miner_fee_sats, miner_fee_blocks, output_public_key)
        serialized_transaction_hex = hexlify(serialized_transaction).decode('utf-8')
        
        return {
            'serialized_transaction': serialized_transaction_hex
        }


