import urllib.request
import json

URL = "https://ingres.iith.ac.in/api/gec/getBusinessDataForUserOpen"
headers = {'Content-Type': 'application/json'}

def try_payload(payload, desc):
    print(f"\n--- Testing: {desc} ---")
    req = urllib.request.Request(URL, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"Status: {response.status}")
            print(f"Items returned: {len(data)}")
            if len(data) > 0:
                print(f"First item locationName: {data[0].get('locationName')}")
    except Exception as e:
        print(f"Error: {e}")

# Base payload variations for Pune
base_uuid = "53e6b3eb-5b23-4416-a193-ca2fa40d9d40"

try_payload({
    "parentLocName": "PUNE", "locname": "PUNE", "loctype": "DISTRICT", "view": "admin",
    "locuuid": base_uuid, "year": "2024-2025", "computationType": "normal",
    "period": "annual", "verificationStatus": 1, "approvalLevel": 1, "parentuuid": base_uuid
}, "view=admin, loctype=DISTRICT")

try_payload({
    "parentLocName": "MAHARASHTRA", "locname": "PUNE", "loctype": "DISTRICT", "view": "admin",
    "locuuid": base_uuid, "year": "2024-2025", "computationType": "normal",
    "period": "annual", "verificationStatus": 1, "approvalLevel": 1, "parentuuid": "e4fe51ab-5d15-4ba2-9214-38ab078864f1" 
    # guessed state uuid... wait, probably not needed if we give parentLocName=MAHARASHTRA
}, "parentLocName=MAHARASHTRA")

try_payload({
    "parentLocName": "INDIA", "locname": "INDIA", "loctype": "COUNTRY", "view": "ADMIN",
    "locuuid": "ffce954d-24e1-494b-ba7e-0931d8ad6085", "year": "2024-2025", "computationType": "normal",
    "period": "annual", "verificationStatus": 1, "approvalLevel": 1, "parentuuid": "ffce954d-24e1-494b-ba7e-0931d8ad6085"
}, "INDIA country-level original trace")

try_payload({
    "parentLocName": "INDIA", "locname": "MAHARASHTRA", "loctype": "STATE", "view": "ADMIN",
    "locuuid": "6038fbc4-83b6-4fd0-83f1-d00db5dd6b30", # random
    "year": "2024-2025"
}, "MAHARASHTRA state level request")
