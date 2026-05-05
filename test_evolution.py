import sys
import os
import asyncio

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import agent

async def main():
    print("--- Testing Self-Improving Evolution Loop ---")
    session_id = "evo_user_456"
    
    # Project 1: Create a lesson
    print("\n[STEP 1] Running Project 1 to generate lessons...")
    req1 = "Create a project 'evolution_1'. Write a python script 'app.py' that calculates Fibonacci. Proceed immediately."
    # Bypass interview for test
    agent.session_states[session_id] = {"state": "EXECUTION", "requirement": req1, "interview_log": []}
    await agent.run_autonomous(req1, session_id)
    
    # Project 2: Check if lessons are loaded
    print("\n[STEP 2] Running Project 2. Checking for experience loading...")
    req2 = "Create a project 'evolution_2'. Just print 'I am smarter now'."
    agent.session_states[session_id] = {"state": "EXECUTION", "requirement": req2, "interview_log": []}
    
    # We will check if the logs show [PAST LESSONS & EXPERIENCE] being loaded
    await agent.run_autonomous(req2, session_id)
    
    # Final check
    lesson_exists = os.path.exists("./memory/lessons/evolution_1_lessons.txt")
    print(f"\nLesson Card Saved: {lesson_exists}")
    
    if lesson_exists:
        with open("./memory/lessons/evolution_1_lessons.txt", "r") as f:
            print("\n--- CONTENT OF LESSON CARD ---")
            print(f.read())

if __name__ == "__main__":
    asyncio.run(main())
