import functions_framework
from flask import escape, request, make_response, jsonify
import jwt
from datetime import datetime, timedelta

# Hardcoded list of users and their passwords for demonstration
USERS = {
    "user1": "pass1",
    "user2": "pass2",
    "user3": "pass3",
    "user4": "pass4",
    "user5": "pass5"
}

# Hardcoded JWT token for simplicity, in a real scenario you'd generate this based on the user
HARDCODED_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkhhcmRjb2RlZCBVc2VyIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

@functions_framework.http
def authenticate_user(request):
    # Set CORS headers for preflight requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers for main requests
    headers = {'Access-Control-Allow-Origin': '*'}

    # Ensure that we have a JSON request
    if request.headers['Content-Type'] == 'application/json':
        request_json = request.get_json(silent=True)
        # Adjust these fields to match the Redux action payload
        username = request_json.get('userId')  # Changed from 'username' to 'userId'
        password = request_json.get('password')

        if username in USERS and USERS[username] == password:
            # Successful authentication
            # For demonstration, returning a hardcoded token; replace with dynamic token generation in real applications
            return jsonify({"token": HARDCODED_TOKEN}), 200, headers
        else:
            # Authentication failed
            return jsonify({"error": "Invalid credentials"}), 401, headers
    else:
        return make_response('Content-Type not supported!', 415, headers)
