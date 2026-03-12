from database.db import get_db_connection
from psycopg2.extras import RealDictCursor

def check_data():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM groundwater_data LIMIT 1")
                row = cur.fetchone()
                print("--- TYPICAL RECORD ---")
                for k, v in row.items():
                    print(f"{k}: {v}")
                
                # Check averages for benchmark calc
                cur.execute("SELECT AVG(rainfall) as avg_rain, AVG(total_recharge) as avg_recharge, AVG(groundwater_extraction_total) as avg_extraction, AVG(extractable_groundwater) as avg_extractable FROM groundwater_data")
                avgs = cur.fetchone()
                print("\n--- GLOBAL AVERAGES IN DB ---")
                print(avgs)
        finally:
            conn.close()

if __name__ == "__main__":
    check_data()
