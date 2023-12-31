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
from session_config import init_session  



log_file_path = '/home/ubuntu/whattogrill-backend/logs/callback_logs.txt'
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,  # Adjust the log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


app = Flask(__name__)
CORS(app, resources={r"/login": {"origins": "https://www.whattogrill.com localhost:8000"},
                      r"/callback": {"origins": "https://www.whattogrill.com localhost:8000"}})

app.secret_key = config.FLASK_SECRET_KEY



# Wrap the Flask app for ASGI compatibility
app_asgi = WsgiToAsgi(app)

redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
print("redis client", redis_client)

@app.route('/login')
async def login():
    print("at /login")

    # Check the initial session data
    print(f"Session Data (Before Redirection): {dict(session)}")

    temp_session_id = os.urandom(24).hex()
    session['temp_session_id'] = temp_session_id

    print("session(sessionid)", session['temp_session_id'])
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
    state = session['temp_session_id']
    print("state", state)
    auth_url = f"{config.COGNITO_DOMAIN}/login?client_id={config.COGNITO_APP_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={config.REDIRECT_URI}&state={state}&code_challenge={code_challenge}&code_challenge_method=S256"
    #auth_url = f"{config.COGNITO_DOMAIN}/login?client_id={config.COGNITO_APP_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={config.REDIRECT_URI}&code_challenge={code_challenge}&code_challenge_method=S256"
    print("auth url", auth_url)
    print("about to redirect")

    # Check session data again before redirection
    print(f"Session Data (Before Redirection): {dict(session)}")

    try:
        return redirect(auth_url)
    except Exception as e:
        print("Redirect error:", e)

@app.route('/callback')
async def callback():
    print("starting /callback")

    # Check session data at the beginning of /callback
    print(f"Session Data (At the Beginning of /callback): {dict(session)}")
    print(f"Code Verifier Retrieved from callback: {session.get('code_verifier')}")

    # Continue with the callback handling
    return await handle_callback(redis_client)  # Pass the Redis client to the handler

@app.route('/dashboard')
def dashboard():
    print("in dashboard")
    if 'username' in session:
        return logged_in(session, redis_client)  # Render the final page
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    init_session(app)
    app.run()