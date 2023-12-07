from database import create_connection, create_tables

def initialize_database():
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        print("Database and tables created successfully.")
        conn.close()
    else:   
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    initialize_database()
