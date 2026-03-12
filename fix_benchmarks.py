import os
import sys
import json

# Absolute path f:\sem 4\edi 2 v2\groundwater_ai
root = r"f:\sem 4\edi 2 v2\groundwater_ai"
sys.path.append(root)

try:
    from database.db import get_db_connection
    from psycopg2.extras import RealDictCursor
    print("Imports successful")
    
    conn = get_db_connection()
    if conn:
        print("Connection successful")
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT district, AVG(rainfall) as rain FROM groundwater_data GROUP BY district LIMIT 5")
            rows = cur.fetchall()
            print(f"Data fetch successful: {len(rows)} districts")
            
            # Logic to update JSON
            b_path = os.path.join(root, "data", "benchmarks.json")
            with open(b_path, 'r') as f:
                data = json.load(f)
            
            # Re-fetch all for real
            cur.execute("""
                SELECT 
                    district,
                    AVG(rainfall) as rain, 
                    AVG(total_recharge) as rech, 
                    AVG(groundwater_extraction_total) as extr, 
                    AVG(extractable_groundwater) as ext_gw, 
                    AVG(agriculture_extraction) as agri 
                FROM groundwater_data 
                GROUP BY district
            """)
            all_rows = cur.fetchall()
            districts = {}
            for r in all_rows:
                d = r['district'].upper()
                ra, re, ex, eg, ag = r['rain'], r['rech'], r['extr'], r['ext_gw'], r['agri']
                if eg and ex:
                    districts[d] = {
                        "name": f"{d} AVG",
                        "stress_index": round((ex/eg)*100, 1),
                        "sustainability_ratio": round(re/ex, 1) if ex else 0,
                        "recharge_efficiency": round(re/ra, 1) if ra else 0,
                        "agri_dependency": round((ag/ex)*100, 1) if ex else 0
                    }
            data["districts"] = districts
            with open(b_path, 'w') as f:
                json.dump(data, f, indent=2)
            print("benchmarks.json updated")
        conn.close()
except Exception as e:
    print(f"FAILED: {e}")
