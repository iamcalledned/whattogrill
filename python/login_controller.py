# login_controller.py
from flask import Flask, redirect, request, session, url_for, render_template, make_response
from flask_cors import CORS
import os
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

log_file_path = '/home/ubuntu/whattogrill-backend/logs/callback_logs.txt'
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,  # Adjust the log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


app = Flask(__name__)
CORS(app, resources={r"/login": {"origins": "https://www.whattogrill.com localhost:8000"}})
app.secret_key = config.FLASK_SECRET_KEY

# Wrap the Flask app for ASGI compatibility
app_asgi = WsgiToAsgi(app)

redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
print("redis client", redis_client)

@app.route('/login')
def login():
    auth_url = f"{config.COGNITO_DOMAIN}/login?client_id={config.COGNITO_APP_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={config.REDIRECT_URI}"
    return redirect(auth_url)

#process the callback from AWS Cognito and attempt to log user in
@app.route('/callback')
def callback():
    return handle_callback(redis_client)  # Pass the Redis client to the handler

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=8080)
    app.run()
