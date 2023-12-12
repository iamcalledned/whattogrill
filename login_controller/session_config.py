#session_config
from flask_session import Session
import redis
from datetime import timedelta


def init_session(app):
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6378, db=0)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Adjust as needed
    app.config['SESSION_COOKIE_NAME'] = 'SessionName'
    app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie
    app.config['SESSION_COOKIE_DOMAIN'] = '.whattogrill.com'



    Session(app)
