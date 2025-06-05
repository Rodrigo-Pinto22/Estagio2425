import psycopg2


def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="ChatbotDB",
        user="postgres",
        password="1234"
    )
    cursor = conn.cursor()
    return conn, cursor