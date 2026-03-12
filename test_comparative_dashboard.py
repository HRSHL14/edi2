from chatbot.chatbot_engine import ChatbotEngine
import json

def test_comparative_dashboard():
    engine = ChatbotEngine()
    print("--- Testing Comparative Dashboard for Amalner ---")
    result = engine.handle_query("amalner report")
    
    # Print the titles of all visuals to verify the dashboard
    print("\nVisuals Generated:")
    for i, vis in enumerate(result.get("visuals", [])):
        print(f"{i+1}. {vis.get('title')} ({vis.get('type')})")
        if vis.get("type") == "bar":
            print(f"   Labels: {vis.get('labels')}")
            for ds in vis.get("datasets", []):
                print(f"   Data: {ds.get('data')}")

if __name__ == "__main__":
    test_comparative_dashboard()
