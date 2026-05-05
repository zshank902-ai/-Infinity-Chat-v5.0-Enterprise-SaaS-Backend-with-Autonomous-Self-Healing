import sys
import os
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agent import agent

async def test_flow():
    session_id = "test_user_123"
    
    print("--- Phase 1: Initial Request ---")
    req1 = "Bhai, mujhe ek simple Weather App banani hai."
    resp1 = await agent.run_autonomous(req1, session_id)
    print(f"User: {req1}")
    print(f"AI: {resp1}\n")
    
    print("--- Phase 2: User Answer ---")
    req2 = "Python use karo aur API openweather use karna."
    resp2 = await agent.run_autonomous(req2, session_id)
    print(f"User: {req2}")
    print(f"AI: {resp2}\n")
    
    print("--- Phase 3: Confirmation ---")
    req3 = "PROCEED"
    print(f"User: {req3}")
    resp3 = await agent.run_autonomous(req3, session_id)
    print(f"AI: [Execution Started... Results will be zipped.]")

if __name__ == "__main__":
    asyncio.run(test_flow())
