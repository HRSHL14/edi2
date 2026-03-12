from chatbot.chatbot_engine import ChatbotEngine
import os

print("Warming ChatbotEngine to populate benchmarks...")
engine = ChatbotEngine()
print("Warming complete.")

# Check if file updated
b_path = os.path.join("data", "benchmarks.json")
if os.path.exists(b_path):
    with open(b_path, 'r') as f:
        import json
        data = json.load(f)
        if "districts" in data:
            print(f"SUCCESS: benchmarks.json now contains {len(data['districts'])} districts.")
        else:
            print("FAILURE: 'districts' key still missing.")
else:
    print(f"FAILURE: {b_path} not found.")
