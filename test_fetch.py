import urllib.request
import json

url = "https://ingres.iith.ac.in/gecdataonline/misview;locname=Pune;loctype=DISTRICT;year=2024-2025"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
        print("Status code:", response.status)
        print("Content length:", len(content))
        with open("test_response.json", "w") as f:
            f.write(content)
except Exception as e:
    print(e)
