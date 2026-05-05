import sys
import os
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agent import agent

async def main():
    print("--- Testing God Mode (Async + Orchestrated + Sandboxed) ---")
    
    requirement = "Create a project 'complex_math'. Write a script 'calc.py' that calculates the first 10 prime numbers, saves them to 'primes.txt', and prints them. Zip the project at the end."
    
    print(f"Task: {requirement}")
    print("Agent is working in God Mode...")
    
    try:
        response = await agent.run_autonomous(requirement)
        print("\n--- Final Agent Response ---")
        print(response[:500] + "...")
        print("\n[GOD MODE] Task completed successfully.")
    except Exception as e:
        print(f"\n[ERROR] God Mode failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
