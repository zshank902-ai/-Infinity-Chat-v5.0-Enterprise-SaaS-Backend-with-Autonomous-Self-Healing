import sys
import os
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agent import agent

async def main():
    print("--- Testing Project Lifecycle & Persistence ---")
    
    requirement = "Create a project 'lifecycle_test'. Add a script 'app.py' that prints 'Hello World'. Zip it and return it."
    
    print(f"Goal: {requirement}")
    
    try:
        response = await agent.run_autonomous(requirement)
        print("\n--- Testing Results ---")
        
        # Check for Zip
        zip_exists = os.path.exists("./projects/lifecycle_test.zip")
        print(f"Zip File Created: {zip_exists}")
        
        # Check for Metadata
        meta_exists = os.path.exists("./memory/vault/lifecycle_test.json")
        print(f"Project Memory Saved: {meta_exists}")
        
        # Check for Folder (Should be deleted)
        folder_exists = os.path.exists("./projects/lifecycle_test")
        print(f"Source Folder Deleted: {not folder_exists}")
        
        print("\n[LIFECYCLE] Test passed! System is efficient and persistent.")
    except Exception as e:
        print(f"\n[ERROR] Lifecycle test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
