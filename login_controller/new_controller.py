# new_login_controller.py
import os
from flask import Flask, redirect
from flask_sockets import Sockets
from config import Config
from asgiref.wsgi import WsgiToAsgi

app = Flask(__name__)
sockets = Sockets(app)

# Only wrap your app with WsgiToAsgi once
app_asgi = WsgiToAsgi(app)

@app.route('/login')
def login():
    auth_url = f"{Config.COGNITO_DOMAIN}/login?client_id={Config.COGNITO_APP_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={Config.REDIRECT_URI}"
    return redirect(auth_url)
