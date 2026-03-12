import json
import csv
import os
import sys
import psycopg2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import get_db_connection

def populate_database():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database. Cannot populate.")
        return

    cur = conn.cursor()
    
    # Optional: Clear existing data for a fresh start
    print("Clearing existing data for a fresh start...")
    cur.execute("TRUNCATE TABLE groundwater_data, talukas, districts, groundwater_raw_json RESTART IDENTITY CASCADE;")
    conn.commit()
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    csv_file = os.path.join(data_dir, 'groundwater_dataset.csv')
    json_file = os.path.join(data_dir, 'raw_response.json')

    # Insert RAW JSON Data
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            raw_data = json.load(f)
            for entry in raw_data:
                district = entry.get('district')
                year = entry.get('year')
                json_data = json.dumps(entry.get('json_data'))
                try:
                    cur.execute("""
                        INSERT INTO groundwater_raw_json (district, year, json_data)
                        VALUES (%s, %s, %s)
                    """, (district, year, json_data))
                except Exception as e:
                    print(f"Error inserting JSON for {district}: {e}")
                    conn.rollback()
        print("Inserted RAW JSON successfully.")

    # Insert Extracted CSV Data
    if os.path.exists(csv_file):
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                district = row['district']
                taluka = row['taluka']
                
                # Insert / Get District ID
                cur.execute("""
                    INSERT INTO districts (district_name) 
                    VALUES (%s) ON CONFLICT (district_name) DO NOTHING
                    RETURNING district_id;
                """, (district,))
                res = cur.fetchone()
                if not res:
                    cur.execute("SELECT district_id FROM districts WHERE district_name = %s", (district,))
                    res = cur.fetchone()
                district_id = res[0]

                # Insert Taluka
                if taluka and taluka != 'Unknown':
                    try:
                        cur.execute("""
                            INSERT INTO talukas (district_id, taluka_name)
                            VALUES (%s, %s) ON CONFLICT (district_id, taluka_name) DO NOTHING
                        """, (district_id, taluka))
                    except Exception as e:
                        print(f"Error inserting taluka {taluka}: {e}")
                        conn.rollback()

                # Insert groundwater_data
                try:
                    cur.execute("""
                        INSERT INTO groundwater_data (
                            district, taluka, rainfall, total_recharge, rainfall_recharge,
                            surface_irrigation_recharge, groundwater_irrigation_recharge, canal_recharge,
                            water_body_recharge, artificial_structure_recharge, extractable_groundwater,
                            groundwater_extraction_total, agriculture_extraction, domestic_extraction,
                            industrial_extraction, natural_discharge, stage_of_extraction, category,
                            future_groundwater_availability, year
                        ) VALUES (
                            %(district)s, %(taluka)s, %(rainfall)s, %(total_recharge)s, %(rainfall_recharge)s,
                            %(surface_irrigation_recharge)s, %(groundwater_irrigation_recharge)s, %(canal_recharge)s,
                            %(water_body_recharge)s, %(artificial_structure_recharge)s, %(extractable_groundwater)s,
                            %(groundwater_extraction_total)s, %(agriculture_extraction)s, %(domestic_extraction)s,
                            %(industrial_extraction)s, %(natural_discharge)s, %(stage_of_extraction)s, %(category)s,
                            %(future_groundwater_availability)s, %(year)s
                        )
                    """, row)
                except Exception as e:
                    print(f"Error inserting groundwater data for {taluka}: {e}")
                    conn.rollback()

        print("Inserted CSV details into PostgreSQL successfully.")
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    populate_database()
