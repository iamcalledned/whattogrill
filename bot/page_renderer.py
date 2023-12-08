# page_renderer.py
from flask import render_template, redirect, url_for, send_from_directory, render_template_string, Response
from auth import generate_nonce
import json
import asyncio
import websockets
import redis
import config
import logging
import os


log_file_path = '/home/ubuntu/whattogrill-backend/logs/page_renderer_logs.txt'
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,  # Adjust the log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)



redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)


async def logged_in(session, redis_client):
    if 'username' in session:
        nonce = generate_nonce()
        session_id = session.get('session_id')
        print("SESSION ID: ", session_id)

        user_info = {}
        if session_id:
            redis_data = redis_client.get(session_id)
            if redis_data:
                user_info = json.loads(redis_data.decode('utf-8'))
            else:
                print("Data not found in Redis for session_id:", session_id)
        else:
            print("Session ID not found in session for user.", user_info)

        print("USER LOGGED IN: ", user_info)

        # Path to your chat.html file
        chat_html_path = '/var/www/html/chat.html'
        if os.path.exists(chat_html_path):
            with open(chat_html_path, 'r') as file:
                chat_html_content = file.read()

            # Render the HTML with dynamic data
            rendered_content = render_template_string(chat_html_content, sessionId=session_id, nonce=nonce, user_info=user_info)
            return Response(rendered_content, mimetype='text/html')
        else:
            return 'chat.html not found', 404
    else:
        return redirect(url_for('login'))
