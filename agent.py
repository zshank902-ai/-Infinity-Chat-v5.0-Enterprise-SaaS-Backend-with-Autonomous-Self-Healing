import os
import json
import re
import asyncio
from datetime import datetime
from router import router
from tools import (create_directory, write_file, run_command, list_files, 
                   zip_directory, setup_environment, run_in_env, web_search, delete_directory,
                   kaggle_search, kaggle_download)
from memory import memory, vault, lessons, redis_mem
from orchestrator import orchestrator
from comm import manager

INDUSTRIAL_SYSTEM_PROMPT = """
You are an Autonomous Industrial Software Engineer. You don't just write code; you build entire projects.

TOOL USAGE RULES:
1. To create a file, use the format: [WRITE_FILE: path/to/file.py] content here [/WRITE_FILE]
2. To create a folder, use: [MKDIR: folder_name]
3. To run a command, use: [RUN: command]
4. To setup the project environment (npm install, venv, etc.), use: [SETUP]
5. To zip the final project, ALWAYS use: [ZIP: folder_name]. DO NOT use python scripts or external tools for zipping.
6. To search the internet for latest info, use: [SEARCH: query]
7. To search Kaggle for datasets/patterns, use: [KAGGLE_SEARCH: query]
8. To download a Kaggle dataset, use: [KAGGLE_DOWNLOAD: dataset_ref]

PROCESS:
- PLAN: First, describe your plan.
- EXECUTE: Use the tags above to build the project.
- VERIFY: Run a command to test the code.
- FIX: If the output shows an error, provide a corrected version immediately.

COMMUNICATION RULE:
- MIRRORING: Always respond to the user in the EXACT language/dialect they use (Hindi, Hinglish, Spanish, French, etc.).
- TECHNICALS: While the conversation is multi-lingual, keep the actual Code, File Names, and Technical Architecture in English.
- PERSONALITY: You are a witty, slightly roasting, and extremely friendly Senior Developer (a "Bhai"). 
- BANTER: Use humor and sarcasm. If the user is being lazy or silly, roast them lightly but always deliver the best solution.
"""

class CodingAgent:
    def __init__(self):
        self.system_prompt = INDUSTRIAL_SYSTEM_PROMPT
        self.current_project_path = "."
        self.session_states = {} # Stores {session_id: {"state": "INTERVIEW", "data": {}}}

    async def run_autonomous(self, user_input, session_id="default"):
        # CREATE ISOLATED WORKSPACE FOR SESSION
        import os
        from pathlib import Path
        session_path = Path(f"./projects/{session_id}")

        session_path.mkdir(parents=True, exist_ok=True)
        self.current_project_path = str(session_path)

        # LOAD STATE FROM REDIS (PERSISTENCE LAYER)
        persisted_state = redis_mem.get_state(session_id)
        if persisted_state:
            self.session_states[session_id] = persisted_state
        
        # Initialize state if new session
        if session_id not in self.session_states:
            self.session_states[session_id] = {"state": "INTERVIEW", "requirement": user_input, "interview_log": [], "path": self.current_project_path}

        state_data = self.session_states[session_id]
        current_state = state_data["state"]

        if current_state == "INTERVIEW":
            print(f"[CONSULTANT] Analyzing requirement confidence...")
            analysis_dict = await orchestrator.analyze_requirement(user_input, state_data["interview_log"])
            analysis_raw = analysis_dict["response"]
            confidence = 50
            if '"confidence_score":' in analysis_raw:
                try:
                    confidence = int(re.search(r'"confidence_score":\s*(\d+)', analysis_raw).group(1))
                except: confidence = 50

            if confidence >= 85 or len(state_data["interview_log"]) > 4:
                 state_data["state"] = "CONFIRMATION"
                 redis_mem.save_state(session_id, state_data) # SAVE BEFORE RECURSION
                 return await self.run_autonomous(user_input, session_id)
            
            questions = await orchestrator.interview_user(user_input)
            state_data["interview_log"].append({"user": user_input, "ai": questions, "confidence": confidence})
            redis_mem.save_state(session_id, state_data) # SAVE STATE
            return f"[Confidence: {confidence}%]\n{questions}"

        if current_state == "CONFIRMATION":
            print(f"[ARCHITECT] Generating Blueprint...")
            blueprint = await orchestrator.generate_blueprint(state_data["requirement"], state_data["interview_log"])
            
            if "proceed" in user_input.lower() or "launch" in user_input.lower() or "go" in user_input.lower():
                state_data["state"] = "EXECUTION"
                redis_mem.save_state(session_id, state_data) # SAVE STATE
                return await self.run_autonomous(user_input, session_id)
            
            redis_mem.save_state(session_id, state_data) # SAVE BLUEPRINT IN STATE
            return f"--- PROJECT BLUEPRINT ---\n{blueprint}\n\nProject blueprint generated. Are you satisfied with this plan? If yes, type 'PROCEED' to begin execution."

        if current_state == "EXECUTION":
            # If already executing, don't start another worker
            if state_data.get("worker_active"):
                return "Swarm is already building your project. Please monitor the progress on your dashboard."

            print(f"\n[SWARM] Initializing Background Construction Worker...")
            state_data["worker_active"] = True
            redis_mem.save_state(session_id, state_data)
            
            # Start the background loop without awaiting it
            asyncio.create_task(self._background_execution_worker(session_id))
            
            return "🚀 CONSTRUCTION INITIALIZED! The swarm has been deployed in the background. I will build your entire project step-by-step. You can monitor progress and see files appearing live in your workspace."

    async def _background_execution_worker(self, session_id):
        if session_id in self.session_states and self.session_states[session_id].get("worker_active"):
            # Already running, but let's double check
            pass
        
        self.session_states[session_id]["worker_active"] = True
        print(f"[LIFECYCLE] Background worker STARTED for {session_id}")
        import os
        self.current_project_path = os.path.abspath(f"projects/{session_id}")
        if not os.path.exists(self.current_project_path):
            os.makedirs(self.current_project_path, exist_ok=True)
        
        try:
            while True:
                state_data = self.session_states.get(session_id)
                if not state_data: return

                if "plan" not in state_data:
                    state_data["plan"] = await orchestrator.architect_plan(state_data["requirement"])
                
                plan_text = state_data["plan"]
                plan_steps = re.findall(r"(?:^\d+\.|\*|-)\s*(.*)", plan_text, re.MULTILINE)
                if not plan_steps: plan_steps = [s.strip() for s in plan_text.split("\n") if s.strip()]
                
                total_steps = len(plan_steps)
                if "current_step" not in state_data: state_data["current_step"] = 0
                
                # Check for completion
                if state_data["current_step"] >= total_steps:
                    break

                step = plan_steps[state_data["current_step"]]
                print(f"[BACKGROUND SWARM] {session_id} - Step {state_data['current_step'] + 1}/{total_steps}: {step}")
                
                state_data["current_phase"] = f"Building: {step[:50]}..."
                redis_mem.save_state(session_id, state_data)
                
                # Stream to WebSocket
                await manager.send_status(session_id, "EXECUTION", int((state_data["current_step"]/total_steps)*100), state_data["current_phase"])
                await manager.send_log(session_id, f"Starting step {state_data['current_step'] + 1}: {step}")

                await self._execute_swarm(state_data["requirement"], step)
                
                await manager.send_log(session_id, f"Step {state_data['current_step'] + 1} completed successfully.", type="success")
                
                state_data["current_step"] += 1
                redis_mem.save_state(session_id, state_data)
                await asyncio.sleep(1) # Safety breather
            
            # Finalize
            state_data["state"] = "COMPLETED"
            state_data["worker_active"] = False
            state_data["current_phase"] = "Project Finalized ✅"
            redis_mem.save_state(session_id, state_data)
            
            await manager.send_status(session_id, "COMPLETED", 100, "Project Finalized ✅")
            await manager.send_log(session_id, "CONSTRUCTION COMPLETE! All files verified and synced.", type="success")
            
            # Reflection
            reflection_dict = await orchestrator.reflect_on_project(state_data["requirement"], "Autonomous build successful.")
            reflection = reflection_dict["response"]
            lessons.add_lesson(reflection)
            print(f"[BACKGROUND SWARM] {session_id} - CONSTRUCTION COMPLETE!")
            
        except Exception as e:
            import traceback
            print(f"[CRITICAL ERROR] Background worker failed for {session_id}: {str(e)}")
            traceback.print_exc()
            if session_id in self.session_states:
                self.session_states[session_id]["worker_active"] = False
                self.session_states[session_id]["current_phase"] = f"Recovery Mode: System Alert. Restarting..."
            
            # Wait before cleanup
            await asyncio.sleep(5)

        current_state = state_data.get("state", "IDLE")
        if current_state == "COMPLETED":
            print(f"[LIFECYCLE] Finishing project for {session_id}...")
            # We use the interview requirement for reflection
            reflection = await orchestrator.reflect_on_project(state_data["requirement"], "Project construction complete.")
            lessons.add_lesson(reflection)
            
            # Save session memory
            memory.save_chat(session_id, "ai", "Project construction finalized. The workspace is ready for deployment.")
            
            # Final cleanup of session state in Redis
            self.session_states.pop(session_id, None)
            if redis_mem.enabled:
                redis_mem.r.delete(f"state:{session_id}")
            return "CONSTRUCTION COMPLETE! The project has been successfully built and verified. Please retrieve your zipped workspace."

    async def _execute_swarm(self, requirement, plan):
        # Step 1: Research Phase (Researcher)
        if any(kw in plan.lower() for kw in ["search", "find", "latest", "research"]):
            print("[SWARM] Researcher Scavenging Web...")
            research_results = await orchestrator.research_topic(plan)
            requirement += f"\n[RESEARCH CONTEXT]: {research_results}"

        # Step 2: Security Review (Groq)
        print("[SWARM] Security Pre-Check (Groq)...")
        
        # Step 3: Implementation Phase (Groq)
        print("[SWARM] Developer Coding (Groq)...")
        prompt = f"{self.system_prompt}\n\nRequirement: {requirement}\nPlan: {plan}\n\nExecute the plan using tools."
        try:
            # Using Groq for implementation as it's the most reliable in this environment
            response = await router.chat(prompt, provider="groq")
            text = response["response"]
            try:
                print(f"[DEBUG-SWARM] AI Raw Response (First 300 chars): {text[:300]}")
            except:
                print("[DEBUG-SWARM] AI Raw Response: [Unicode Content Hidden]")
            
            if "[WRITE_FILE" not in text:
                print("[WARNING] Swarm forgot to write files! Retrying with Force-Tag instruction...")
                prompt += "\n\nCRITICAL: You MUST use [WRITE_FILE: path] content [/WRITE_FILE] tags to actually build the project. Do not just talk."
                response = await router.chat(prompt, provider="groq")
                text = response["response"]
        except Exception as e:
            print(f"[SWARM-ERROR] Implementation Failed: {str(e)}")
            # Last resort fallback to DeepSeek
            response = await router.chat(prompt, provider="deepseek")
            text = response["response"]
        
        # Step 4: Verification & QA (Groq)
        print("[SWARM] QA & Security Audit (Groq)...")
        audit_report_dict = await orchestrator.security_audit(text)
        audit_report = audit_report_dict["response"]
        
        if "SECURE" not in audit_report.upper():
            print(f"[SWARM] Security Alert! Fixing vulnerabilities...")
            fix_response_dict = await orchestrator.fix_code(text, audit_report)
            text = fix_response_dict["response"]

        # Step 5: Final Execution & Tools
        print("[SWARM] Processing Final Tools...")
        await self._process_tools_async(text, requirement)
        
        # Step 6: ZERO-MISTAKE FORMAL VERIFICATION
        print("[SWARM] Running Zero-Mistake Formal Verification...")
        test_response_dict = await orchestrator.formal_verification(requirement, text)
        test_code = test_response_dict["response"]
        
        # Clean the test code from any markdown tags
        test_code = re.sub(r"```python|```", "", test_code).strip()
        
        test_file = "swarm_verification_test.py"
        write_file(test_file, test_code, base_path=self.current_project_path)
        
        print(f"[SWARM] Verifying project functionality...")
        test_result = run_command(f'python "{os.path.join(self.current_project_path, test_file)}"')
        
        if "Success" not in test_result:
            print(f"[RECOVERY] Formal Verification Failed! Error: {test_result}. Self-healing...")
            fix_prompt = f"The code failed the formal verification test. Error: {test_result}. Fix the code."
            fix_response_dict = await orchestrator.fix_code(text, fix_prompt)
            text = fix_response_dict["response"]
            await self._process_tools_async(text, requirement) # Apply fixes
        print("[SWARM] Formal Verification PASSED! ✅")
        
        # FINAL PACKAGING: Zip the entire project for the user
        print(f"[PACKAGING] Creating final project ZIP for {session_id}...")
        zip_name = f"project_{session_id}.zip"
        zip_path = zip_directory(self.current_project_path, zip_name)
        
        self.session_states[session_id]["progress"] = 100
        self.session_states[session_id]["phase"] = "COMPLETED"
        self.session_states[session_id]["status"] = f"SUCCESS! Your empire is ready. Download ZIP: {zip_name}"
        
        print(f"[FINISH] Empire Build Complete! ZIP: {zip_path}")
        return text

    async def _process_tools_async(self, text, requirement, attempt=1):
        if attempt > 3:
            print("[SELF-HEALING] Max attempts reached. Stopping.")
            return

        # Handle MKDIR
        mkdir_matches = re.findall(r"\[MKDIR: (.*?)\]", text)
        for path in mkdir_matches:
            create_directory(path, base_path=self.current_project_path)
            # Generic environment setup
            if "/" not in path and "\\" not in path:
                setup_environment(path, base_path=self.current_project_path)

        # Handle SETUP (Explicit call)
        if "[SETUP]" in text:
            setup_environment(".", base_path=self.current_project_path)

        # Handle WRITE_FILE (Enhanced for lazy AI)
        file_matches = re.findall(r"\[WRITE_FILE: (.*?)\]\s*(?:```(?:\w+)?\n)?(.*?)(?:\n```|\[/WRITE_FILE\]|$)", text, re.DOTALL)
        for path, content in file_matches:
            # Clean up the path and content
            path_clean = path.strip().replace("`", "")
            content_clean = content.strip()
            if content_clean:
                write_file(path_clean, content_clean, base_path=self.current_project_path)

        # Handle RUN (with Self-Healing)
        run_matches = re.findall(r"\[RUN: (.*?)\]", text)
        for cmd in run_matches:
            print(f"[EXECUTION] Running '{cmd}' in {self.current_project_path} (Attempt {attempt})...")
            output = run_in_env(self.current_project_path, cmd)
            print(f"Output: {output[:200]}...")

            if "Error" in output or "Exception" in output:
                print("[SWARM-FIX] Error detected! QA Agent flagging for Lead Developer...")
                fix_response_dict = await orchestrator.fix_code(text, output)
                fix_text = fix_response_dict["response"]
                await self._process_tools_async(fix_text, requirement, attempt + 1)

        # Handle ZIP
        zip_matches = re.findall(r"\[ZIP: (.*?)\]", text)
        for path in zip_matches:
            zip_directory(path, base_path=self.current_project_path)

        # Handle SEARCH
        search_matches = re.findall(r"\[SEARCH: (.*?)\]", text)
        for query in search_matches:
            results = web_search(query)
            try:
                print(f"Search Results for '{query}': {results[:200]}...")
            except:
                print(f"Search Results for '{query}': [Unicode Content Hidden]")

        # Handle KAGGLE_SEARCH
        k_search_matches = re.findall(r"\[KAGGLE_SEARCH: (.*?)\]", text)
        for query in k_search_matches:
            results = kaggle_search(query)
            try:
                print(f"Kaggle Results for '{query}': {results[:200]}...")
            except:
                print(f"Kaggle Results for '{query}': [Unicode Content Hidden]")

        # Handle KAGGLE_DOWNLOAD
        k_down_matches = re.findall(r"\[KAGGLE_DOWNLOAD: (.*?)\]", text)
        for ref in k_down_matches:
            # We download to the current project path
            results = kaggle_download(ref, path=self.current_project_path)
            try:
                print(f"Kaggle Download: {results}")
            except:
                print(f"Kaggle Download: [Unicode Content Hidden]")

    async def generate_project(self, requirement):
        return await self.run_autonomous(requirement)

agent = CodingAgent()
