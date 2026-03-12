
import sys
import os
import json

# Add the project root to sys.path
sys.path.append(os.getcwd())

from chatbot.chatbot_engine import ChatbotEngine

def test_hardened_dashboard():
    engine = ChatbotEngine()
    
    # Test for Amalner
    query = "Sustainability and Stress for Amalner"
    print(f"Testing Query: {query}")
    
    response = engine.handle_query(query)
    
    explanation = response.get("explanation", "")
    visuals = response.get("visuals", [])
    
    print(f"\nNumber of visuals: {len(visuals)}")
    
    # Check Table Content for State Efficiency
    print("\nChecking Table for State Efficiency...")
    if "Efficiency" in explanation and "MH: 32.6" in explanation:
        print("SUCCESS: State Efficiency (32.6) found in table.")
    else:
        print("FAILURE: State Efficiency not found or incorrect in table.")
        # Find the Efficiency line specifically
        for line in explanation.split("\n"):
            if "Efficiency" in line:
                print(f"Actual Efficiency Line: {line}")
    
    # Check visuals for clean names
    expected_labels = ["Amalner", "Jalgaon", "Maharashtra", "India"]
    
    print("\nChecking Chart Labels...")
    for vis in visuals:
        if vis.get("type") == "bar" and len(vis.get("labels", [])) == 4:
            labels = vis.get("labels")
            print(f"Chart: {vis['title']} Labels: {labels}")
            if labels == expected_labels:
                print("SUCCESS: Labels match expected clean names.")
            else:
                print(f"WARNING: Labels {labels} do not match {expected_labels}")
                
    # Sectoral Pie
    sector_chart = next((v for v in visuals if "Sector-wise Use" in v['title']), None)
    if sector_chart:
        print(f"\nSectoral Pie Labels: {sector_chart.get('labels')}")
        if sector_chart.get("type") == "pie":
            print("SUCCESS: Sectoral chart type is Pie.")

if __name__ == "__main__":
    test_hardened_dashboard()
