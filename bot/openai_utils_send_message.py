#openai_utils_send_message.py
from openai import OpenAI
import os
import time

# Initialize OpenAI client
openai_client = OpenAI()
openai_client.api_key = os.getenv("OPENAI_API_KEY")  # Ensure you have set this environment variable


#send the message    
def send_message(thread_id_n, message):
    try:
        response = openai_client.beta.threads.messages.create(
            thread_id_n,
            role="user",
            content=message
        )
        # Extracting the response text from the nested structure
        response_text = response.content[0].text.value
        
        print("response for thread:", thread_id_n)
        return response_text
    except Exception as e:
        print(f"Error in sending message: {e}")
        return "Error in sending message."
