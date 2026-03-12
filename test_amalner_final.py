from chatbot.chatbot_engine import ChatbotEngine
import json

def test_amalner_final():
    engine = ChatbotEngine()
    print("--- Testing Amalner Report for Comparison Table ---")
    result = engine.handle_query("amalner report")
    
    print("\nExplanation (Snippet):")
    print(result.get("explanation", "")[:500])
    
    # Check if table has 3 columns (roughly)
    has_benchmark_col = "Benchmark" in result.get("explanation", "")
    print(f"\nBenchmark Column in Table: {has_benchmark_col}")
    
    print("\nVisuals Generated:")
    for v in result.get("visuals", []):
        print(f"- {v.get('title')}")

if __name__ == "__main__":
    test_amalner_final()
