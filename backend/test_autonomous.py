import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agent import agent
from backend.tools import BASE_PROJECT_PATH

def test_autonomous_mode():
    print("--- Testing Autonomous Agent Mode ---")
    
    requirement = "Create a project named 'test_bot'. Inside it, create a file 'bot.py' that prints 'I am alive!' and run it."
    
    print(f"Task: {requirement}")
    print("Agent is thinking and working...")
    
    response = agent.run_autonomous(requirement)
    
    print("\n--- Agent Response ---")
    print(response)
    
    print("\n--- Verification ---")
    bot_file = BASE_PROJECT_PATH / "test_bot" / "bot.py"
    if bot_file.exists():
        print(f"[SUCCESS] File {bot_file} was created by the agent!")
    else:
        print(f"[FAILED] File {bot_file} was not found.")

if __name__ == "__main__":
    test_autonomous_mode()
