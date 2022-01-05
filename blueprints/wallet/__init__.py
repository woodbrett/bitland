'''
Created on Dec 29, 2021

@author: prakasha
'''

from flask import Blueprint, request, render_template, make_response, redirect, url_for
from node.networking.peering_functions import authenticateLocalUser
from wallet.information import getWalletUtxos

from system_variables import (
    override_ip_to_allow_remote_wallet_access,
    )

blueprint = Blueprint('wallet', __name__, url_prefix='/wallet')

@blueprint.route('/')
def index():
    isAuthenticated = request.cookies.get('authenticated')
    if isAuthenticated == 'True':
        return redirect(url_for('wallet.dashboard'))
    else:
        return render_template('login.html')

@blueprint.route('/login')
def login():
    error = request.args.get('error')
    return render_template('login.html', error=error)

@blueprint.route('/authenticate', methods = ['POST'])
def authenticate():
    password = request.form['password']
    ip = request.remote_addr
    if override_ip_to_allow_remote_wallet_access : ip = '127.0.0.1'
    if authenticateLocalUser(ip, password) == False:
        return redirect(url_for('wallet.login', error='Invalid password'))
    else:
        utxos = getWalletUtxos()
        resp = make_response(render_template('utxos.html', utxos=utxos.get('utxos')))
        resp.set_cookie('authenticated', 'True')
        return resp
    
@blueprint.route('/dashboard', methods = ['GET'])
def dashboard():
    if request.cookies.get('authenticated') == 'True':
        return redirect(url_for('wallet.utxos'))
    else:
        return redirect(url_for('wallet.login'))
    
@blueprint.route('/mywallet', methods = ['GET'])
def wallet():
    if request.cookies.get('authenticated') == 'True':
        return render_template('mywallet.html')
    else:
        return redirect(url_for('wallet.login'))
    
@blueprint.route('/utxos', methods = ['GET'])
def utxos():
    if request.cookies.get('authenticated') == 'True':
        utxos = getWalletUtxos()
        return render_template('utxos.html', utxos=utxos.get('utxos'))
    else:
        return redirect(url_for('wallet.login'))
    
@blueprint.route('/logout', methods = ['GET'])
def logout():
    resp = make_response(render_template('login.html'))
    resp.set_cookie('authenticated', 'False')
    return resp
    



