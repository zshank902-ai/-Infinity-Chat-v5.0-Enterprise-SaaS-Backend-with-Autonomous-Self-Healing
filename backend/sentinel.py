import asyncio
import time
from router import router
from config import config

class InfinitySentinel:
    def __init__(self):
        self.status = "HEALTHY"
        self.last_check = time.time()
        self.errors = []

    async def check_api_health(self):
        """Check if at least one AI provider is responsive."""
        try:
            # Simple ping to primary provider
            response = await router.chat("ping", provider="groq")
            if response:
                return True
        except Exception as e:
            self.errors.append(f"API Health Error: {str(e)}")
            return False

    async def run_smoke_test(self):
        """Perform a lightweight end-to-end logic test."""
        from agent import agent
        try:
            # Mock a small request
            test_req = "Test: Create a file named sentinel.txt"
            session_id = "sentinel_test"
            agent.session_states[session_id] = {"state": "EXECUTION", "requirement": test_req}
            # Note: We won't actually run the full build to save tokens, 
            # just check if orchestrator can plan.
            from orchestrator import orchestrator
            plan = await orchestrator.architect_plan(test_req)
            if plan:
                return True
        except Exception as e:
            self.errors.append(f"Smoke Test Error: {str(e)}")
            return False

    async def monitor_loop(self):
        """Infinite loop to guard the system."""
        while True:
            api_ok = await self.check_api_health()
            smoke_ok = await self.run_smoke_test()
            
            if api_ok and smoke_ok:
                self.status = "HEALTHY"
            else:
                self.status = "DEGRADED"
                print(f"[SENTINEL ALERT] System status is {self.status}. Errors: {self.errors[-1]}")
            
            self.last_check = time.time()
            await asyncio.sleep(600) # Check every 10 minutes

sentinel = InfinitySentinel()
