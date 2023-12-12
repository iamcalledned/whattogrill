#session_config
from flask_session import Session
import redis

def init_session(app):
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_REDIS'] = redis.Redis(host='0.0.0.0', port=6379, db=0)
    Session(app)
