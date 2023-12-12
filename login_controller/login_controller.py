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

#session_config.init_session(app)





app.secret_key = config.FLASK_SECRET_KEY

# Wrap the Flask app for ASGI compatibility
app_asgi = WsgiToAsgi(app)

redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
print("redis client", redis_client)

#@app.after_request
#def after_request(response):
#    for key, value in session.items():
#        print("f-key")
#        print(f"{key}: {type(value)} - {value}")
#    return response

@app.route('/login')

async def login():
    print("at /login")
    try:
        session_config.init_session(app)
        print("Session initialization was successful.")
    except Exception as e:
        print(f"An error occurred during session initialization: {str(e)}")


    # Generate a code verifier
    code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8')
    print("code verifier", code_verifier)
    print("code verifier type", type(code_verifier))
    session['code_verifier'] = code_verifier

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
        print("Error redirecting:", e)
        return "Redirect failed"


@app.route('/get_session_data')
async def get_session_data():
    print("at /get_session_data")
    # Assuming session_id and nonce are stored in the Flask session or similar
    session_id = session.get('session_id')
    print("SESSION ID: ", session_id)
    nonce = session.get('nonce')
    user_info = session.get('user_info')  # Adjust as per your actual session keys
    print("user info from get session data", user_info)

    return jsonify(sessionId=session_id, nonce=nonce, userInfo=user_info)



#process the callback from AWS Cognito and attempt to log user in
@app.route('/callback')
async def callback():
    print("starting /callback")
    
    # Check if the user already has a valid session
    session_id = session.get('session_id')
    print("SESSION ID from callback: ", session_id)
    temp_session_id = session.get('session_id')
    #if session_id:
        # Check if the session exists in Redis
    #    print("we have a valid session")
    #    redis_data = redis_client.get(session_id)
    #    print("redis data", redis_data)
    #    if redis_data:
    #        user_info = json.loads(redis_data.decode('utf-8'))
    #        # Validate the user_info (you can add more checks as needed)
    #        if 'username' in user_info and 'email' in user_info:
    #            # If session and user info are valid, redirect to the desired page
    #            return await logged_in(session, redis_client)
                
    return await handle_callback(redis_client)  # Pass the Redis client to the handler

@app.route('/dashboard')
def dashboard():
    print("in dashboard")
    if 'username' in session:
        return logged_in(session, redis_client)  # Render the final page
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8080)
    app.run()
