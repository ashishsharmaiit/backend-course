import functions_framework
from flask import request, make_response, jsonify
from markupsafe import escape
import jwt
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

USERS = {
    "ashish": "sharma",
    "vihang": "agarwal",
    "anagh": "deshpande",
}

HARDCODED_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

@functions_framework.http
def authenticate_user(request):
    if request.method == 'OPTIONS':
        headers = ...
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}

    if request.headers['Content-Type'] == 'application/json':
        request_json = request.get_json(silent=True)
        username = request_json.get('userId')
        password = request_json.get('password')

        logging.info(f'Authenticating user: {username}')  # Log the username being authenticated

        if username in USERS and USERS[username] == password:
            logging.info(f'User authenticated: {username}')  # Log successful authentication
            return jsonify({"token": HARDCODED_TOKEN}), 200, headers
        else:
            logging.warning(f'Invalid credentials for user: {username}')  # Log failed authentication
            return jsonify({"error": "Invalid credentials"}), 401, headers
    else:
        logging.error('Unsupported Content-Type')
        return make_response('Content-Type not supported!', 415, headers)
