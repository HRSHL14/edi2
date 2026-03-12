import os
import sys
import json

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

try:
    from database.db import get_db_connection
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("Error: Could not import database modules.")
    sys.exit(1)

def update_benchmarks():
    conn = get_db_connection()
    if not conn:
        print("Error: Could not connect to database.")
        return

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
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
                ORDER BY district
            """)
            rows = cur.fetchall()
            
            district_benchmarks = {}
            for r in rows:
                name = r['district'].upper()
                rain, rech, extr, ext_gw, agri = r['rain'], r['rech'], r['extr'], r['ext_gw'], r['agri']
                
                if ext_gw and extr:
                    stress = round((extr/ext_gw)*100, 1)
                    sust = round(rech/extr, 1) if extr else 0
                    eff = round(rech/rain, 1) if rain else 0
                    agri_dep = round((agri/extr)*100, 1) if extr else 0
                    
                    district_benchmarks[name] = {
                        "name": f"{name} AVG",
                        "stress_index": stress,
                        "sustainability_ratio": sust,
                        "recharge_efficiency": eff,
                        "agri_dependency": agri_dep
                    }

            # Load existing benchmarks
            b_path = os.path.join("data", "benchmarks.json")
            if os.path.exists(b_path):
                with open(b_path, 'r') as f:
                    data = json.load(f)
            else:
                data = {}

            # Add districts
            data["districts"] = district_benchmarks
            
            with open(b_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Successfully updated {len(district_benchmarks)} district benchmarks in {b_path}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_benchmarks()
