# new_login_controller.py
import sys
import os
from flask import Flask
from flask_sockets import Sockets
from flask import redirect
import config


app = Flask(__name__)
sockets = Sockets(app)

@app.route('/login')
def login():
    auth_url = f"{config.COGNITO_DOMAIN}/login?client_id={config.COGNITO_APP_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={config.REDIRECT_URI}"
    return redirect(auth_url)

# In your login_controller.py
app_asgi = app