import psycopg2
import json
import os

try:
    conn = psycopg2.connect(
        host="127.0.0.1", 
        port="5432", 
        database="groundwater_db", 
        user="postgres", 
        password="hsp14"
    )
    cur = conn.cursor()
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
    rows = cur.fetchall()
    
    districts = {}
    for r in rows:
        d = r[0].upper()
        ra, re, ex, eg, ag = r[1], r[2], r[3], r[4], r[5]
        if eg and ex:
            districts[d] = {
                "name": f"{d} AVG",
                "stress_index": round((ex/eg)*100, 1),
                "sustainability_ratio": round(re/ex, 1) if ex else 0,
                "recharge_efficiency": round(re/ra, 1) if ra else 0,
                "agri_dependency": round((ag/ex)*100, 1) if ex else 0
            }
            
    b_path = r"f:\sem 4\edi 2 v2\groundwater_ai\data\benchmarks.json"
    with open(b_path, 'r') as f:
        data = json.load(f)
    
    data["districts"] = districts
    
    with open(b_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Updated {len(districts)} districts")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
