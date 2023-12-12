# auth.py
import sys
import os
# Get the directory of the current script
current_script_path = os.path.dirname(os.path.abspath(__file__))
# Set the path to the parent directory (one folder up)
parent_directory = os.path.dirname(current_script_path)
# Add the config directory to sys.path
sys.path.append(os.path.join(parent_directory, 'config'))

import base64
import requests
import jwt
import json
from jwt.algorithms import RSAAlgorithm
import config
import logging
import gevent
import base64
from urllib.parse import urlencode
import redis
from flask import session, request
import session_config



# Cognito Configuration
COGNITO_USER_POOL_ID = config.COGNITO_USER_POOL_ID
COGNITO_APP_CLIENT_ID = config.COGNITO_APP_CLIENT_ID
COGNITO_DOMAIN = config.COGNITO_DOMAIN
REDIRECT_URI = config.REDIRECT_URI

log_file_path = config.LOG_PATH

redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)

logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,  # Adjust the log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def print_code_verifier(temp_session_id):
    # Retrieve the session data from Redis
    print("temp_session_id", temp_session_id)
    session_data_json = redis_client.get(temp_session_id)
    
    if session_data_json:
        # Deserialize the session data
        session_data = json.loads(session_data_json)
        
        # Access and print the code_verifier
        code_verifier = session_data.get('code_verifier')
        if code_verifier:
            print(f"Code Verifier for session {temp_session_id}: {code_verifier}")
        else:
            print(f"Code verifier not found in session data for session {temp_session_id}")
    else:
        print(f"No session data found for session ID: {temp_session_id}")


def generate_nonce():
    return base64.b64encode(os.urandom(16)).decode('utf-8')

def exchange_code_for_token(code):
    token_url = f"{COGNITO_DOMAIN}/oauth2/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    for key, value in session.items():
        print(f"Session Key: {key}, Session Value: {value}")
    data = {
        'grant_type': 'authorization_code',
        'client_id': COGNITO_APP_CLIENT_ID,
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'code_verifier': request.args.get('code_verifier')
    }
    print("data", data)
    encoded_data = urlencode(data)

    # Log the final request data for debugging (be cautious of sensitive info)
    logging.debug(f"Token request data: {encoded_data}")
    print(f"Token request data: {encoded_data}")
    try:
        response = requests.post(token_url, headers=headers, data=encoded_data)
        if response.status_code == 200:
            #session.pop('code_verifier', None)  # Remove the code verifier
            return response.json()
        else:
            logging.error(f"Token exchange failed with status {response.status_code}: {response.text}")
            print(f"Token exchange failed with status {response.status_code}: {response.text}")
            return None
    except requests.RequestException as e:
        #session.pop('code_verifier', None)
        logging.error(f"Error contacting token endpoint: {str(e)}")
        print(f"Error contacting token endpoint: {str(e)}")
        return None

def validate_token(id_token):
    jwks_url = f"https://cognito-idp.us-east-1.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    jwks_response = requests.get(jwks_url)
    jwks = jwks_response.json()

    headers = jwt.get_unverified_header(id_token)
    kid = headers['kid']
    key = [k for k in jwks['keys'] if k['kid'] == kid][0]
    pem = RSAAlgorithm.from_jwk(json.dumps(key))

    decoded_token = jwt.decode(
        id_token,
        pem,
        algorithms=['RS256'],
        audience=COGNITO_APP_CLIENT_ID
    )
    return decoded_token

