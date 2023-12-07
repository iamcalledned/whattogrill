import requests
import json
import re
import html
import websocket

def send_message_to_server(user_id, message, user_ip):
    ws_url = 'wss://yourdomain.com:8055/api/send_message'  # Use your domain
    payload = {
        'userID': user_id,
        'message': message,
        'user_ip': user_ip
    }

    try:
        # Create a new WebSocket connection
        ws = websocket.create_connection(ws_url)

        # Send the message
        ws.send(json.dumps(payload))

        # Receive the server's response
        response = ws.recv()
        ws.close()

        return json.loads(response)
    except Exception as e:
        return {"response": f"Error: {str(e)}"}


def strip_html_tags(text):
    """Remove HTML tags and convert HTML entities to plain text."""
    clean_text = re.sub('<.*?>', '', text)  # Remove HTML tags
    return html.unescape(clean_text)  # Convert HTML entities to plain text

def main():
    user_id = 'test_user8'
    user_ip = '127.0.0.127'
    while True:
        message = input("Enter your message: ")
        if message.lower() == 'exit':
            print("Exiting program.")
            break
        print(message)
        response = send_message_to_server(user_id, message, user_ip)
        formatted_response = strip_html_tags(response['response'])  # Assuming 'response' is the key for the text
        print("\nResponse from server:", formatted_response)

if __name__ == "__main__":
    main()
