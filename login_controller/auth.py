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


# Cognito Configuration
COGNITO_USER_POOL_ID = config.COGNITO_USER_POOL_ID
COGNITO_APP_CLIENT_ID = config.COGNITO_APP_CLIENT_ID
COGNITO_DOMAIN = config.COGNITO_DOMAIN
REDIRECT_URI = config.REDIRECT_URI

log_file_path = '/home/ubuntu/iamcalledned-backend/logs/authorization_logs.txt'

logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,  # Adjust the log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def generate_nonce():
    return base64.b64encode(os.urandom(16)).decode('utf-8')

def exchange_code_for_token(code):
    token_url = f"{COGNITO_DOMAIN}/oauth2/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'client_id': COGNITO_APP_CLIENT_ID,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    try:
        response = requests.post(token_url, headers=headers, data=data)
        return response.json() if response.status_code == 200 else None
    except requests.RequestException as e:
        raise Exception(f"Error contacting token endpoint: {str(e)}")

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

