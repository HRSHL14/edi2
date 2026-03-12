import psycopg2
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT

def verify_data():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM districts")
        districts_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM talukas")
        talukas_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM groundwater_data")
        data_count = cur.fetchone()[0]
        
        print(f"Districts: {districts_count}")
        print(f"Talukas: {talukas_count}")
        print(f"Groundwater Data Rows: {data_count}")
        
        if data_count > 0:
            print("\nSample Data (First 3 rows):")
            cur.execute("SELECT district, taluka, rainfall, category FROM groundwater_data LIMIT 3")
            for row in cur.fetchall():
                print(row)
                
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error verifying data: {e}")

if __name__ == "__main__":
    verify_data()
