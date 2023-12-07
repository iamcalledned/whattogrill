import sqlite3

def run_query(db_file, query, params=None):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Execute the query with parameters (if any)
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    # Fetch and print all the records
    records = cursor.fetchall()
    for record in records:
        print(record)

    # Close the connection
    conn.close()

if __name__ == '__main__':
    db_file = 'C:/Users/lengu/Documents/GitHub/whattogrill/chatbot.db'

    # Query the users table
    print("Users Table:")
    run_query(db_file, "SELECT * FROM users;")

    # Query the threads table
    print("\nThreads Table:")
    run_query(db_file, "SELECT * FROM threads;")

    print("\nconversations table:")
    # Example usage with a parameter (replace 1 with the actual UserID you want to query)
    run_query(db_file, "SELECT * FROM conversations")
