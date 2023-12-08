#openai_utils_new_thread.py
from openai import OpenAI
import os

# Initialize OpenAI client
openai_client = OpenAI()
openai_client.api_key = os.getenv("OPENAI_API_KEY")

async def create_thread_in_openai():
    try:
        thread_response = openai_client.beta.threads.create()
        thread_id_n = thread_response.id
        print("Created new thread ID:", thread_id_n)
        return thread_id_n
    except Exception as e:
        print(f"Error in creating thread: {e}")
        return None

async def is_thread_valid(thread_id):
    try:
        my_thread = openai_client.beta.threads.retrieve(thread_id)
        # Add your logic here based on how OpenAI's response indicates a valid thread.
        # This might depend on the response structure. For example:
        # return 'status' in my_thread and my_thread.status == 'active'
        return True  # Assuming the thread is valid if no exception occurred
    except Exception as e:
        print(f"Error checking thread validity: {e}")
        return False
