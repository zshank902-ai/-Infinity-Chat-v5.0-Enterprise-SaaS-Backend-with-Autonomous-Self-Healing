import asyncio
import sys
from agent import agent
from memory import redis_mem

# Force UTF-8 for Windows Terminal
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

async def full_power_loop():
    print("\n=== INFINITY CHAT v5.0: LEGENDARY POWER MODE ===")
    session_id = "legendary_build_001"
    
    # REQUIREMENT
    requirement = "Create a project 'crypto_tracker'. Build fetcher.py (fetches BTC price from Coingecko), data.json, and a beautiful index.html. ZIP the whole folder 'crypto_tracker'."
    
    print(f"Project: {requirement}")
    print("Status: Initiating Swarm Lifecycle...\n")
    
    user_input = "GO"
    
    # LOOP UNTIL COMPLETION
    while True:
        response = await agent.run_autonomous(user_input, session_id=session_id)
        print(f"\n--- SYSTEM RESPONSE ---\n{response}\n")
        
        if "CONSTRUCTION COMPLETE" in response:
            print("\nMISSION ACCOMPLISHED: The project is built, verified, and zipped.")
            break
            
        # Continue signal
        user_input = "GO"
        
        # Small delay to prevent API spam
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(full_power_loop())
