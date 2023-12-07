# page_renderer.py
import sys
import os
# Get the directory of the current script
current_script_path = os.path.dirname(os.path.abspath(__file__))
# Set the path to the parent directory (one folder up)
parent_directory = os.path.dirname(current_script_path)
# Add the config directory to sys.path
sys.path.append(os.path.join(parent_directory, 'config'))
from flask import render_template, redirect, url_for
from auth import generate_nonce
import json
import asyncio
import websockets
import redis
import config
import logging


log_file_path = '/home/ubuntu/whattogrill-backend/logs/page_renderer_logs.txt'
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,  # Adjust the log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)



redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)


def logged_in(session, redis_client):
    if 'username' in session:
        
        nonce = generate_nonce()
        
        # Get session_id from the current session
        session_id = session.get('session_id')
        
        
        if session_id:
            # Attempt to retrieve data from Redis based on session_id
            redis_data = redis_client.get(session_id)
            
            if redis_data:
                # Parse the JSON data retrieved from Redis
                user_info = json.loads(redis_data.decode('utf-8'))
                
                
                # Establish a WebSocket connection asynchronously
                #run_async_connect_to_chatbot(session_id, session['username'])
                #print("WebSocket connection initiated")
                
            else:
                # Handle the case when data is not found in Redis
                user_info = {}
                print("Data not found in Redis for session_id:", session_id)
        else:
            # Handle the case when session_id is not found in the current session
            user_info = {}
            print("Session ID not found in session for user.", user_info)

        
        print("USER LOGGED IN: ", user_info)
        return render_template('chat.html', sessionId=session_id, nonce=nonce, user_info=user_info)
    else:
        return redirect(url_for('login'))
