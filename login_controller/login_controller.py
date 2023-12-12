# login_controller.py
import sys
import os
# Get the directory of the current script
current_script_path = os.path.dirname(os.path.abspath(__file__))
# Set the path to the parent directory (one folder up)
parent_directory = os.path.dirname(current_script_path)
# Add the config directory to sys.path
sys.path.append(os.path.join(parent_directory, 'config'))
sys.path.append(os.path.join(parent_directory, 'bot'))
from flask import Flask, redirect, request, session, url_for, render_template, make_response, jsonify, Response
from flask_cors import CORS
import redis
import json
from auth import generate_nonce, exchange_code_for_token, validate_token
import config
from callback_handler import handle_callback
import asyncio
import websockets
from page_renderer import logged_in
from asgiref.wsgi import WsgiToAsgi
import logging
import gevent
import hashlib
import base64
import session_config



log_file_path = '/home/ubuntu/whattogrill-backend/logs/callback_logs.txt'
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,  # Adjust the log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


app = Flask(__name__)
CORS(app, resources={r"/login": {"origins": "https://www.whattogrill.com localhost:8000"},
                      r"/get_session_data": {"origins": "https://www.whattogrill.com localhost:8000"}})

app.secret_key = config.FLASK_SECRET_KEY

# Wrap the Flask app for ASGI compatibility
app_asgi = WsgiToAsgi(app)

redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
print("redis client", redis_client)

@app.route('/login')
async def login():
    print("at /login")
    
    session_id = os.urandom(24).hex()
    session['session_id'] = session_id
    
    print("session(sessionid)", session['session_id'])
    # Generate a code verifier
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
    print("code verifier", code_verifier)
    print("code verifier type", type(code_verifier))
    session['code_verifier'] = code_verifier
    print(f"Code Verifier Retrieved from login: {session.get('code_verifier')}")

    # Generate a code challenge
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.replace('+', '-').replace('/', '_').replace('=', '')
    print("code challenge", code_challenge)
    print("code challenge type", type(code_challenge))

    # Construct the Cognito URL with the code challenge
    auth_url = f"{config.COGNITO_DOMAIN}/login?client_id={config.COGNITO_APP_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={config.REDIRECT_URI}&code_challenge={code_challenge}&code_challenge_method=S256"
    print("auth url", auth_url)
    print("about to redirect")
    response = Response()
    response.headers['Location'] = auth_url
    try:
        return redirect(auth_url)
    except Exception as e:
        print("Redirect error:", e)

@app.route('/callback')
async def callback():
    print("starting /callback")
    
    return await handle_callback(redis_client)  # Pass the Redis client to the handler

@app.route('/dashboard')
def dashboard():
    print("in dashboard")
    if 'username' in session:
        return logged_in(session, redis_client)  # Render the final page
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()