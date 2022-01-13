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
from mining.mining_functions import getTransactionsFromMempool

namespace = Namespace('mempool', 'Mempool')

@namespace.route('/mempoolTransactions')
class get_mempool_transactions(Resource):

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self,ip_address,port):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')

        mempool_transactions = getTransactionsFromMempool()
        
        return {
            'mempool_transactions': mempool_transactions
        }

