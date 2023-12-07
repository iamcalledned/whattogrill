#chat_bot_soceket
import sys
import os
# Get the directory of the current script
current_script_path = os.path.dirname(os.path.abspath(__file__))
# Set the path to the parent directory (one folder up)
parent_directory = os.path.dirname(current_script_path)
# Add the config directory to sys.path
sys.path.append(os.path.join(parent_directory, 'database'))
sys.path.append(os.path.join(parent_directory, 'config'))
import redis
import asyncio
import json
import websockets
import ssl
import logging
from uuid import uuid4
from datetime import datetime, timezone
from openai_utils_generate_answer import generate_answer
import config


# Other imports as necessary

log_file_path = '/home/ubuntu/whattogrill-backend/logs/chat_bot_logs.txt'
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,  # Adjust the log level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Initialize Redis client
redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)

async def chatbot_handler(websocket, path):
    try:
        # Initial message should contain session_id
        initial_data = await websocket.recv()
        initial_data = json.loads(initial_data)

        session_id = initial_data.get('session_id', '')
        if session_id:
            # Retrieve user information from Redis
            user_info = redis_client.get(session_id)
            if user_info:
                user_info = json.loads(user_info.decode('utf-8'))
                # Now you have user's information like user_name, username, and name
                userID = user_info['username']
                # ... You can use this user information as needed ...
            else:
                # Handle case where session_id is not valid or user info not found
                # For example, send a message back to the client indicating the issue
                await websocket.send(json.dumps({'error': 'Invalid session'}))
                return  # Optionally, close the connection
        else:
            # Handle case where session_id is not sent in the initial message
            await websocket.send(json.dumps({'error': 'Session ID required'}))
            return  # Optionally, close the connection

        while True:
            # Continue with normal message handling
            data = await websocket.recv()
            data = json.loads(data)  # Assuming the data is JSON formatted

            userID = user_info.get('username', '')  # Using username from Redis
            
            uuid = str(uuid4())  # generate a new UUID for the request
            message = data.get('message', '')
            user_ip = websocket.remote_address[0]  # Get client IP address

            # Assuming generate_answer is a function you've defined
            response_text = generate_answer(userID, message, user_ip)

            # Prepare the response
            response = {
                'response': response_text
            }
            # Send the response back to the client
            await websocket.send(json.dumps(response))

            logging.info(f"Processed message from {user_ip}")
    except websockets.exceptions.ConnectionClosed:
        logging.info("Connection closed")

if __name__ == '__main__':
    server_address = '172.31.91.113'
    server_port = 8055

    # Create an SSL context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain('/home/ubuntu/whattogrill-backend/fullchain.pem', '/home/ubuntu/whattogrill-backend/privkey.pem')


    # Start the WebSocket server
    start_server = websockets.serve(chatbot_handler, server_address, server_port, ssl=ssl_context)

    logging.info('Starting WebSocket server...')
    print("Starting Websocket at:", server_address, server_port,ssl_context)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
