
import sys
import os
import json

# Add the project root to sys.path
sys.path.append(os.getcwd())

from chatbot.chatbot_engine import ChatbotEngine

def test_unified_visuals():
    engine = ChatbotEngine()
    
    # Test for Amalner (Single Region)
    query = "Sustainability Index, Recharge vs Extraction, Stage Gauge, Sector Pie, Groundwater Stress Index, Recharge Efficiency for Amalner"
    print(f"Testing Query: {query}")
    
    response = engine.handle_query(query)
    
    # print(json.dumps(response, indent=2))
    
    explanation = response.get("explanation", "")
    visuals = response.get("visuals", [])
    
    print(f"\nExplanation length: {len(explanation)}")
    print(f"Number of visuals generated: {len(visuals)}")
    
    expected_titles = [
        "Sustainability Index Benchmarking",
        "Recharge vs Extraction Balance (MCM)",
        "Stage of Extraction Benchmarking (%)",
        "Sectoral Usage Comparison (%)",
        "Groundwater Stress Index Benchmarking (%)",
        "Recharge Efficiency Benchmarking"
    ]
    
    found_titles = [v.get("title") for v in visuals]
    
    print("\nVisuals Found:")
    for title in found_titles:
        print(f"- {title}")
        
    missing = [t for t in expected_titles if t not in found_titles]
    if not missing:
        print("\nSUCCESS: All 6 unified comparison visuals are present!")
    else:
        print(f"\nFAILURE: Missing visuals: {missing}")
        
    # Check if visuals have the right labels (4 levels)
    if visuals:
        first_vis = visuals[0]
        labels = first_vis.get("labels", [])
        print(f"\nLabels in first visual: {labels}")
        if len(labels) >= 3:
            print("SUCCESS: 3+ levels represented in labels (Taluka, State, Nation).")
        else:
            print("WARNING: Fewer than 3 levels found in labels.")

if __name__ == "__main__":
    test_unified_visuals()
