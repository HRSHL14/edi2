from chatbot.chatbot_engine import ChatbotEngine
import json

def test_pune_benchmarks():
    engine = ChatbotEngine()
    print("--- Testing Pune Report with Benchmarks ---")
    result = engine.handle_query("pune report")
    print(json.dumps(result, indent=2))
    
    # Check if visuals contain benchmarking
    has_benchmark = any("Benchmarking" in v.get("title", "") for v in result.get("visuals", []))
    print(f"\nBenchmarking Visual Found: {has_benchmark}")

if __name__ == "__main__":
    test_pune_benchmarks()
