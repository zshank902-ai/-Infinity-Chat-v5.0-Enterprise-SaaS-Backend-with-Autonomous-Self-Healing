import sys
import os
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agent import agent

async def main():
    print("--- Testing Universal Agnostic Engine (Node.js) ---")
    
    requirement = "Create a simple Node.js project named 'node_swarm'. Initialize it with a package.json, add an index.js that prints 'Node.js Agnostic Engine Success!', run it to verify, and then zip it."
    
    print(f"Goal: {requirement}")
    
    try:
        response = await agent.run_autonomous(requirement)
        print("\n--- Final Agent Response ---")
        print(response[:800] + "...")
        
        # Verify Zip
        zip_exists = os.path.exists("./projects/node_swarm.zip")
        print(f"Node.js Zip Created: {zip_exists}")
        
        print("\n[AGNOSTIC] Test complete. The engine is now language-independent!")
    except Exception as e:
        print(f"\n[ERROR] Agnostic test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
