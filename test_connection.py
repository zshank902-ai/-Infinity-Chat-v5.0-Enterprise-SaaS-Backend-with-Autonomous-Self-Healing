import sys
import os

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.router import router
from backend.agent import agent

def test_apis():
    print("--- Testing API Router ---")
    
    # Test 1: Simple Chat
    print("\n1. Testing Simple Chat (Primary Provider)...")
    response = router.chat("Hello! Are you working?")
    print(f"Response: {response}")

    # Test 2: DeepSeek (Optional, if key exists)
    print("\n2. Testing DeepSeek Chat...")
    try:
        ds_response = router.chat("Write a fast sorting algorithm in Python.", provider="deepseek")
        print(f"DeepSeek Response Snippet:\n{ds_response[:200]}...")
    except Exception as e:
        print(f"DeepSeek Test Skipped/Failed: {e}")

    # Test 3: Industrial Agent
    print("\n3. Testing Industrial Coding Agent...")
    project_req = "Create a simple Python Flask API with one GET endpoint."
    project_response = agent.generate_project(project_req)
    print(f"Agent Response Snippet:\n{project_response[:500]}...")

if __name__ == "__main__":
    test_apis()
