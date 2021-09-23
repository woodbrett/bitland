'''
Created on Mar 28, 2021

@author: brett_wood
'''

from flask import request
from flask_restplus import Namespace, Resource, fields, Api
from http import HTTPStatus
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.wrappers import Response
from node.networking.peering_functions import authenticateLocalUser
from node.information.blocks import getKmlLandbaseByBlock


namespace = Namespace('blockchain_data', 'Blockchain Data')

#only available to local user
@namespace.route('/getKmlLandbase/<int:block_height>')
class get_block(Resource):
    '''Get kml file showing the landbase polygon for a specific block'''

    @namespace.response(500, 'Internal Server error')
    @namespace.doc(security='Bearer')   
    def get(self, block_height):
        
        if authenticateLocalUser(request.remote_addr, request.headers.get("Authorization")) == False:
            namespace.abort(400, 'Not authenticated')
        
        kml = getKmlLandbaseByBlock(block_height)
        
        response = Response(kml, mimetype='text/kml')
        response.headers.set("Content-Disposition", "attachment", filename="landbase_" + str(block_height) + ".kml")
        
        return response




