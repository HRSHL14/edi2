import json
import urllib.request
import csv
import os
import time

# Updated UUIDs from browser trace (2024-2025)
MAHARASHTRA_UUID = "e7b3f02d-2497-4bcd-9e20-baa4b621822b"
DISTRICTS = {
    "Ahmednagar": "39479641-fa67-4329-b39d-4d011c142305",
    "Akola": "a58d13d8-7f34-4337-9207-b7b84e4cabc4",
    "Amravati": "f4f8a4f0-26e9-41c9-8803-03b67a0ded98",
    "Aurangabad": "1fdacc9c-b57f-4a8f-b8e4-5c152013dfdb",
    "Beed": "12500a79-2886-4c00-82a1-e476e115e138",
    "Bhandara": "ba251b46-48f0-477e-98d7-72dcd37e4ba2",
    "Buldhana": "fb1a7c84-b3a2-479d-8bbb-8c1172429998",
    "Chandrapur": "8a70a946-2c55-4580-bcd6-7757cec7b6c4",
    "Dhule": "0d0b0581-0483-4c59-933a-2cd9e7a0974a",
    "Gadchiroli": "ac4c984a-0d91-4537-89a3-1be8c0d07377",
    "Gondia": "d7b247af-f077-4e02-8821-562806615c4b",
    "Hingoli": "095def2b-84e3-4a23-a376-1925ef352cf2",
    "Jalgaon": "004f685f-028e-4a54-89b5-617c294aa0e6",
    "Jalna": "56517b40-daaa-41f6-ac60-5a91d65e6053",
    "Kolhapur": "fe6d8004-7765-43b6-a2ab-00dbd825312b",
    "Latur": "692181cb-dadd-47bd-83bb-af325f412f98",
    "Mumbai": "41c79fd7-75fb-4ba6-813b-0dfbb34f3ce9",
    "Mumbai Suburban": "2899a103-a1fa-45a9-bc23-df7d4d6d5671",
    "Nagpur": "68d0f469-947f-404d-b7d7-dd38c93e6a77",
    "Nanded": "55816d79-28d2-477a-90dd-74ea5a01374d",
    "Nandurbar": "4c96182c-d163-4d6d-ad0d-da7edb63a60a",
    "Nashik": "7a59f50c-2b31-47cf-a2d9-9d11ca370774",
    "Osmanabad": "708f4e94-7a06-4fb9-91a1-1580a5eac39b",
    "Palghar": "0cc1d612-cccb-4cc2-9a99-c10886df5452",
    "Parbhani": "36efdd06-5294-4d77-93c8-51ca35e372fe",
    "Pune": "471dff0a-9b41-46f2-890d-179b2408ca4d",
    "Raigad": "7d2da05f-709a-4551-89e0-44b957195cf7",
    "Ratnagiri": "08907f95-6749-4507-af26-54b7969cc78a",
    "Sangli": "56f671d0-343d-4858-b697-38c512e813e0",
    "Satara": "ef1da758-3804-42e4-b4de-166cace8fe28",
    "Sindhudurg": "771c33ee-bfef-4622-a694-ffdf37d0a427",
    "Solapur": "f769253a-5a18-450c-9988-8e766cb23909",
    "Thane": "0c5585b1-ed3c-41fc-8159-309e81fba895",
    "Wardha": "0e3abc8d-261a-4510-8163-2deece193976",
    "Washim": "c43bd47a-3c44-40f2-b0c5-1f070bfbca62",
    "Yavatmal": "8324058f-6dc6-42ac-85c2-34bdc3c06d1a"
}

YEAR = "2024-2025"
POST_URL = "https://ingres.iith.ac.in/api/gec/getBusinessDataForUserOpen"

def fetch_and_process():
    # Correct pathing for f:\sem 4\edi 2 v2\groundwater_ai
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    raw_json_file = os.path.join(data_dir, "raw_response.json")
    csv_file = os.path.join(data_dir, "groundwater_dataset.csv")

    all_raw_data = []
    parsed_records = []
    
    headers = [
        "district", "taluka", "rainfall", "total_recharge", "rainfall_recharge", 
        "surface_irrigation_recharge", "groundwater_irrigation_recharge", 
        "canal_recharge", "water_body_recharge", "artificial_structure_recharge", 
        "extractable_groundwater", "groundwater_extraction_total", 
        "agriculture_extraction", "domestic_extraction", "industrial_extraction", 
        "natural_discharge", "stage_of_extraction", "category", 
        "future_groundwater_availability", "year"
    ]

    req_headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for district_name, district_uuid in DISTRICTS.items():
        print(f"Fetching data for {district_name}...")
        
        payload = {
            "locname": district_name,
            "loctype": "DISTRICT",
            "locuuid": district_uuid,
            "component": "recharge",
            "period": "annual",
            "stateuuid": None,
            "category": "all",
            "year": YEAR,
            "view": "admin",
            "computationType": "normal",
            "verificationStatus": 1,
            "approvalLevel": 1,
            "parentuuid": MAHARASHTRA_UUID
        }

        try:
            req = urllib.request.Request(POST_URL, data=json.dumps(payload).encode('utf-8'), headers=req_headers, method='POST')
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8')
                data = json.loads(content)
                
                all_raw_data.append({
                    "district": district_name,
                    "year": YEAR,
                    "json_data": data
                })
                
                taluka_count = 0
                for block in data:
                    # Skip "total" row if present
                    if block.get("locationName") == "total":
                        continue
                    
                    try:
                        record = {h: 0.0 for h in headers}
                        record["district"] = district_name
                        record["year"] = YEAR
                        record["taluka"] = block.get("locationName", "Unknown")
                        # Rainfall extraction (handles dict or float)
                        rainfall_data = block.get("rainfall")
                        if isinstance(rainfall_data, dict):
                            record["rainfall"] = rainfall_data.get("total", 0.0)
                        else:
                            record["rainfall"] = rainfall_data or 0.0
                        
                        # Recharge Data
                        recharge = block.get("rechargeData") or {}
                        record["total_recharge"] = (recharge.get("total") or {}).get("total", 0.0)
                        record["rainfall_recharge"] = (recharge.get("rainfall") or {}).get("total", 0.0)
                        record["surface_irrigation_recharge"] = (recharge.get("surface_irrigation") or {}).get("total", 0.0)
                        record["groundwater_irrigation_recharge"] = (recharge.get("gw_irrigation") or {}).get("total", 0.0)
                        record["canal_recharge"] = (recharge.get("canal") or {}).get("total", 0.0)
                        record["water_body_recharge"] = (recharge.get("water_body") or {}).get("total", 0.0)
                        record["artificial_structure_recharge"] = (recharge.get("artificial_structure") or {}).get("total", 0.0)
                        
                        # Extraction / Draft Data
                        draft = block.get("draftData") or {}
                        record["groundwater_extraction_total"] = (draft.get("total") or {}).get("total", 0.0)
                        record["agriculture_extraction"] = (draft.get("agriculture") or {}).get("total", 0.0)
                        record["domestic_extraction"] = (draft.get("domestic") or {}).get("total", 0.0)
                        record["industrial_extraction"] = (draft.get("industry") or {}).get("total", 0.0)
                        
                        # Stage of Extraction (handles dict or float)
                        soe_data = block.get("stageOfExtraction")
                        if isinstance(soe_data, dict):
                            record["stage_of_extraction"] = soe_data.get("total", 0.0)
                        else:
                            record["stage_of_extraction"] = soe_data or 0.0

                        # Future Availability (handles dict or float)
                        fav_data = block.get("availabilityForFutureUse")
                        if isinstance(fav_data, dict):
                            record["future_groundwater_availability"] = fav_data.get("total", 0.0)
                        else:
                            record["future_groundwater_availability"] = fav_data or 0.0

                        # Current Availability (handles dict or float)
                        cav_data = block.get("currentAvailabilityForAllPurposes")
                        if isinstance(cav_data, dict):
                            record["extractable_groundwater"] = cav_data.get("total", 0.0)
                        else:
                            record["extractable_groundwater"] = cav_data or 0.0

                        # Category (handles dict or str)
                        cat_data = block.get("category")
                        if isinstance(cat_data, dict):
                            record["category"] = cat_data.get("total", "Unknown")
                        else:
                            record["category"] = cat_data or "Unknown"

                        record["natural_discharge"] = (record["total_recharge"] - record["extractable_groundwater"]) if record["total_recharge"] else 0.0

                        parsed_records.append(record)
                        taluka_count += 1
                    except Exception as parse_e:
                        print(f"  Warning: Could not parse taluka in {district_name}. Err: {parse_e}")
                
                print(f"  Downloaded {taluka_count} talukas for {district_name}")
                # Brief sleep to avoid rate limiting
                time.sleep(1)
                        
        except Exception as e:
            print(f"  Error fetching {district_name}: {e}")

    # Save RAW JSON
    with open(raw_json_file, "w") as f:
        json.dump(all_raw_data, f, indent=4)
        
    # Save CSV
    with open(csv_file, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(parsed_records)

    print(f"\nIngestion successful! Processed {len(all_raw_data)} districts and {len(parsed_records)} talukas.")

if __name__ == "__main__":
    fetch_and_process()
