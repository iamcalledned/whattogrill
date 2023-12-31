# callback_handler.py
import sys
import os
# Get the directory of the current script
current_script_path = os.path.dirname(os.path.abspath(__file__))
# Set the path to the parent directory (one folder up)
parent_directory = os.path.dirname(current_script_path)
# Add the config directory to sys.path
sys.path.append(os.path.join(parent_directory, 'config'))
from flask import Flask, redirect, request, session, url_for, render_template, make_response
from auth import exchange_code_for_token, validate_token, generate_nonce, print_code_verifier
import config
import json
import redis
from page_renderer import logged_in
import logging
import asyncio
import gevent
import traceback




# Configure logging with an absolute path for the log file
log_file_path = '/home/ubuntu/whattogrill-backend/logs/callback_logs.txt'
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,  # Adjust the log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)



async def handle_callback(redis_client):
    print("redis client", redis_client)
    print("in callback")
    
    code = request.args.get('code')
    print("code:", code)
    state = request.args.get('state')
    print("state from callback:", state)
    temp_session_id = state
    #print("Current stack trace:")
    #traceback.print_stack()
    # Retrieve session data before checking the code
    print(f"Code Verifier Retrieved from callback: {session.get('code_verifier')}")
    temp_session_id_redis = print_code_verifier(temp_session_id)
    print("test session id:", temp_session_id_redis)
    for key, value in session.items():
        print(f"Session Key in callback: {key}, Session Value: {value}")
    if code:
        try:
            tokens = exchange_code_for_token(code)
            print("tokens:", tokens)
            if tokens:
                id_token = tokens['id_token']
                decoded_token = validate_token(id_token)
                
                # Store user information in session
                session['email'] = decoded_token.get('email', 'unknown')
                session['username'] = decoded_token.get('cognito:username', 'unknown')
                session['name'] = decoded_token.get('name', 'unknown')
                print("made it to logged in")
                
                # Attempt to save data to Redis
                session_id = os.urandom(24).hex()
                session['session_id'] = str(session_id)
                session['session_id'] = session_id
                print("session ID type",type(session_id))
                print("session sessionID", session['session_id'])

                
                user_info = {'username': session['username'], 'email': session['email'], 'name': session['name'], 'session_id': session['session_id']}
                redis_set_result = redis_client.set(session_id, json.dumps(user_info))
                print("redis set result:", redis_set_result)
                print("session id from redis:", redis_client.get(session_id))
                if not redis_set_result:
                    return 'Failed to save data to Redis.', 500
                print("going to logged_in")
                return redirect(url_for('dashboard'))
                #return logged_in(session, redis_client)  # Call the function from login_controler
            else:   
                return 'Error during token exchange.', 400
        except Exception as e:
            return f"Token validation error: {str(e)}", 400

    return 'Authentication failed or cancelled.', 400
