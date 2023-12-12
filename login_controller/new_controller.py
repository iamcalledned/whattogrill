# new_login_controller.py
import sys
import os
# Get the directory of the current script
current_script_path = os.path.dirname(os.path.abspath(__file__))
# Set the path to the parent directory (one folder up)
parent_directory = os.path.dirname(current_script_path)
# Add the config directory to sys.path
sys.path.append(os.path.join(parent_directory, 'config'))
sys.path.append(os.path.join(parent_directory, 'bot'))
from flask import Flask
from flask_sockets import Sockets
from flask import redirect


app = Flask(__name__)
sockets = Sockets(app)

@app.route('/login')
def login():
    auth_url = f"{config.COGNITO_DOMAIN}/login?client_id={config.COGNITO_APP_CLIENT_ID}&response_type=code&scope=openid&redirect_uri={config.REDIRECT_URI}"
    return redirect(auth_url)

# In your login_controller.py
app_asgi = app