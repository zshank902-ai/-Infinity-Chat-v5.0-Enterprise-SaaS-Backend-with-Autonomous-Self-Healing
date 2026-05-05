import asyncio
from agent import agent
from memory import redis_mem

async def full_power_demonstration():
    print("\n--- INFINITY CHAT v5.0: FULL POWER MODE ---")
    session_id = "power_test_001"
    
    # FORCE OVERRIDE STATE TO EXECUTION
    state_data = {
        "state": "EXECUTION",
        "requirement": "Build a real-time Crypto Portfolio Tracker. Create fetcher.py, data.json, and index.html. Zip the folder 'crypto_tracker'.",
        "interview_log": [{"user": "Start", "ai": "Bypassing interview for demo."}],
        "plan": "1. Create crypto_tracker directory\n2. Create fetcher.py with API logic\n3. Create data.json\n4. Create index.html dashboard\n5. Zip the results",
        "current_step": 0
    }
    redis_mem.save_state(session_id, state_data)
    
    print("Status: Manual Override Active. Swarm Launched in EXECUTION MODE.\n")
    
    # Run the agent in autonomous mode
    response = await agent.run_autonomous("PROCEED WITH FULL BUILD", session_id=session_id)
    
    print("\n--- AGENT FINAL REPORT ---")
    print(response)

if __name__ == "__main__":
    asyncio.run(full_power_demonstration())
