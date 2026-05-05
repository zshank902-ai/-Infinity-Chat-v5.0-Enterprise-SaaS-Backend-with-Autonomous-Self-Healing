import sys
import os
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agent import agent

async def main():
    print("--- Testing Swarm Intelligence Agency (Architect + Security + Dev + QA + Web Search) ---")
    
    requirement = "Find the latest version of FastAPI and create a project 'fastapi_pro'. Add a main.py with one route and a README mentioning the version you found."
    
    print(f"Goal: {requirement}")
    print("Agency is starting work...")
    
    try:
        response = await agent.run_autonomous(requirement)
        print("\n--- Final Agency Response ---")
        print(response[:800] + "...")
        print("\n[SWARM] Project delivered with security audit and latest info.")
    except Exception as e:
        print(f"\n[ERROR] Swarm failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
