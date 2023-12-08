# callback_handler.py
import sys
import os
# Get the directory of the current script
current_script_path = os.path.dirname(os.path.abspath(__file__))
# Set the path to the parent directory (one folder up)
parent_directory = os.path.dirname(current_script_path)
# Add the config directory to sys.path
sys.path.append(os.path.join(parent_directory, 'config'))
from flask import Flask, redirect, request, session, url_for, render_template, make_response, jsonify
from auth import exchange_code_for_token, validate_token, generate_nonce
import config
import json
import redis
from page_renderer import logged_in
import logging
import asyncio
import gevent


# Configure logging with an absolute path for the log file
log_file_path = '/home/ubuntu/whattogrill-backend/logs/callback_logs.txt'
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,  # Adjust the log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def handle_callback(redis_client):
    print("in callback")
    code = request.args.get('code')
    print("code:", code)
    if code:
        try:
            tokens = exchange_code_for_token(code)
            if tokens:
                id_token = tokens['id_token']
                decoded_token = validate_token(id_token)

                # Store user information in session
                session['email'] = decoded_token.get('email', 'unknown')
                session['username'] = decoded_token.get('cognito:username', 'unknown')
                session['name'] = decoded_token.get('name', 'unknown')

                # Generate a new session ID or retrieve the existing one
                session_id = session.get('session_id', os.urandom(24).hex())
                session['session_id'] = session_id
                user_info = {
                    'username': session['username'],
                    'email': session['email'],
                    'name': session['name'],
                    'session_id': session_id
                }

                # Save or update the session data in Redis
                redis_set_result = redis_client.set(session_id, json.dumps(user_info))
                if redis_set_result:
                    # If the session is saved successfully, proceed to the logged_in flow
                    return await logged_in(session, redis_client)  # This will handle existing sessions
                else:
                    # If saving the session fails, return an error
                    return jsonify({'error': 'Failed to save session data'}), 500
            else:
                # If token exchange fails, return an error
                return jsonify({'error': 'Error during token exchange'}), 400
        except Exception as e:
            # If an exception occurred, return an error
            return jsonify({'error': f'Token validation error: {str(e)}'}), 400
    else:
        # If no code parameter is provided, return an error
        return jsonify({'error': 'Authentication failed or cancelled'}), 400

# Define your logged_in function here if it's not already defined