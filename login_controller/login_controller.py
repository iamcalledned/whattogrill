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
from flask import Flask, redirect, request, session, url_for, render_template, make_response, jsonify
from flask_cors import CORS
import redis
import json
from auth import generate_nonce, exchange_code_for_token, validate_token
import config
from callback_handler import handle_callback
import asyncio
import websockets
import page_renderer
from asgiref.wsgi import WsgiToAsgi
import logging
import gevent



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
    auth_url = f"{config.COGNITO_DOMAIN}/login?client_id={config.COGNITO_APP_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={config.REDIRECT_URI}"
    return redirect(auth_url)


@app.route('/get_session_data')
def get_session_data():
    print("at /get_session_data")
    # Assuming session_id and nonce are stored in the Flask session or similar
    session_id = session.get('session_id')
    nonce = session.get('nonce')
    user_info = session.get('user_info')  # Adjust as per your actual session keys
    print("user info from get session data", user_info)

    return jsonify(sessionId=session_id, nonce=nonce, userInfo=user_info)



#process the callback from AWS Cognito and attempt to log user in
@app.route('/callback')
async def callback():
    print("at /callback")
####maybe add a check hre to see if the user is already logged in
    # Get session data
    response = get_session_data()
    session_data = response.get_json()
    existing_session_id = session_data.get('sessionId')
    print("existing session id at beginning of callback", existing_session_id)

    return await handle_callback(redis_client, existing_session_id)  # Pass the Redis client to the handler

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8080)
    app.run()
