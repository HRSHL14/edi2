import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT

def create_database():
    try:
        # Connect to default 'postgres' database to create the new one
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname='postgres',
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(f'CREATE DATABASE {DB_NAME}')
            print(f"Database {DB_NAME} created successfully.")
        else:
            print(f"Database {DB_NAME} already exists.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_database()
