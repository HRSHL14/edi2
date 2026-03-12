
import sys
import os
import json

# Add the project root to sys.path
sys.path.append(os.getcwd())

from chatbot.chatbot_engine import ChatbotEngine

def diag():
    engine = ChatbotEngine()
    response = engine.handle_query("report for Amalner")
    print("TABLE ROWS:")
    if "explanation" in response:
        for line in response["explanation"].split("\n"):
            if "Efficiency" in line:
                print(line)
    
    print("\nBENCHMARKS LOADED:")
    print(json.dumps(engine.get_benchmarks("Jalgaon"), indent=2))

if __name__ == "__main__":
    diag()
