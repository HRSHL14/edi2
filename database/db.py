import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            connect_timeout=5
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
                with open(schema_path, 'r') as f:
                    cur.execute(f.read())
            conn.commit()
            print("Database schema initialized successfully.")
        except Exception as e:
            print(f"Error initializing schema: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    init_db()
