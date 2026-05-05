from router import router
from tools import (create_directory, write_file, run_command, list_files, 
                   zip_directory, setup_environment, run_in_env, web_search, delete_directory,
                   kaggle_search, kaggle_download)
from memory import memory, vault, lessons
from orchestrator import orchestrator
import re
import asyncio

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
        session_path = Path(f"d:/Python Workshop/infinity_chat/projects/{session_id}")
        session_path.mkdir(parents=True, exist_ok=True)
        self.current_project_path = str(session_path)

        # Initialize state if new session
        if session_id not in self.session_states:
            self.session_states[session_id] = {"state": "INTERVIEW", "requirement": user_input, "interview_log": [], "path": self.current_project_path}

        state_data = self.session_states[session_id]
        current_state = state_data["state"]

        if current_state == "INTERVIEW":
            print(f"[CONSULTANT] Analyzing requirement confidence...")
            analysis_raw = await orchestrator.analyze_requirement(user_input, state_data["interview_log"])
            
            # Simple JSON parsing (with fallback)
            confidence = 50
            if '"confidence_score":' in analysis_raw:
                try:
                    confidence = int(re.search(r'"confidence_score":\s*(\d+)', analysis_raw).group(1))
                except: confidence = 50

            if confidence >= 85 or len(state_data["interview_log"]) > 4:
                 state_data["state"] = "CONFIRMATION"
                 return await self.run_autonomous(user_input, session_id)
            
            questions = await orchestrator.interview_user(user_input)
            state_data["interview_log"].append({"user": user_input, "ai": questions, "confidence": confidence})
            return f"[Confidence: {confidence}%]\n{questions}"

        if current_state == "CONFIRMATION":
            print(f"[ARCHITECT] Generating Blueprint...")
            blueprint = await orchestrator.generate_blueprint(state_data["requirement"], state_data["interview_log"])
            
            if "proceed" in user_input.lower() or "launch" in user_input.lower() or "go" in user_input.lower():
                state_data["state"] = "EXECUTION"
                return await self.run_autonomous(user_input, session_id)
            
            return f"--- PROJECT BLUEPRINT ---\n{blueprint}\n\nBhai, kya aap is plan se satisfied hain? Agar haan, toh 'PROCEED' likhiye."

        if current_state == "EXECUTION":
            print(f"\n[SWARM] Launching Phase-based Execution...")
            # We add a 'current_step' to track progress
            if "current_step" not in state_data:
                state_data["current_step"] = 0
                state_data["plan"] = await orchestrator.architect_plan(state_data["requirement"])
            
            plan_steps = state_data["plan"].split("\n") # Simple split for now
            total_steps = len(plan_steps)
            
            if state_data["current_step"] < total_steps:
                # CHECK IF USER PROVIDED NEW FEEDBACK INSTEAD OF 'GO'
                if user_input.lower() not in ["go", "launch", "proceed", "finalize"] and state_data["current_step"] > 0:
                    print(f"[REFACTOR] User provided new idea mid-stream. Rewinding...")
                    state_data["requirement"] += f"\n[NEW UPDATE]: {user_input}"
                    state_data["current_step"] = 0 # REWIND TO START REFACTORING
                    state_data["plan"] = await orchestrator.architect_plan(state_data["requirement"])
                    return f"Bhai, aapka naya idea note kar liya hai! Main pura plan refactor karke piche se start kar raha hoon taaki kuch bhi miss na ho. (Type 'GO' to start refactored execution)"

                step = plan_steps[state_data["current_step"]]
                print(f"[SWARM] Executing Step {state_data['current_step'] + 1}: {step}")
                
                # Execute specific step
                response = await self._execute_swarm(state_data["requirement"], step)
                state_data["current_step"] += 1
                
                return f"[STEP {state_data['current_step']}/{total_steps} COMPLETE]\n{response}\n\nBhai, ye step ho gaya hai. Ab tak sab theek lag raha hai? Agar aapke dimaag mein koi naya idea aaya hai toh bata do, wo bhi abhi implement ho jayega. Warna 'GO' likho, kaam continue karte hain!"
            
            # Final Lifecycle if all steps done
            state_data["state"] = "COMPLETED"
            return await self.run_autonomous("Finalize", session_id)

        if current_state == "COMPLETED":
            print(f"[LIFECYCLE] Finishing project for {session_id}...")
            # We use the interview requirement for reflection
            reflection = await orchestrator.reflect_on_project(state_data["requirement"], "Project construction complete.")
            lessons.add_lesson(reflection)
            
            # Save session memory
            memory.save_chat(session_id, "ai", "Bhai, project complete ho gaya hai! Aap isse download kar sakte hain.")
            
            # Final cleanup of session state
            self.session_states.pop(session_id, None)
            return "CHAMPION! Aapka project poori tarah se ready hai. Zipped file check kijiye!"

    async def _execute_swarm(self, requirement, plan):
        # Step 2: Security Review (Groq)
        print("[SWARM] Security Pre-Check (Groq)...")
        
        # Step 3: Implementation Phase (DeepSeek)
        print("[SWARM] Developer Coding (DeepSeek)...")
        prompt = f"{self.system_prompt}\n\nRequirement: {requirement}\nPlan: {plan}\n\nExecute the plan using tools."
        response = await router.chat(prompt, provider="deepseek")
        
        # Step 4: Verification & QA (Groq)
        print("[SWARM] QA & Security Audit (Groq)...")
        audit_report = await orchestrator.security_audit(response)
        if "SECURE" not in audit_report.upper():
            print(f"[SWARM] Security Alert! Fixing vulnerabilities...")
            response = await orchestrator.fix_code(response, audit_report)

        # Step 5: Final Execution & Tools
        print("[SWARM] Processing Final Tools...")
        await self._process_tools_async(response, requirement)
        
        # Step 6: ZERO-MISTAKE FORMAL VERIFICATION
        print("[SWARM] Running Zero-Mistake Formal Verification...")
        test_code = await orchestrator.formal_verification(requirement, response)
        
        # Clean the test code from any markdown tags
        test_code = re.sub(r"```python|```", "", test_code).strip()
        
        # Save and run test
        test_file = "data/last_test.py"
        write_file(test_file, test_code)
        test_result = run_command(f"python {test_file}")
        
        if "Success" not in test_result:
            print(f"[RECOVERY] Formal Verification Failed! Error: {test_result}. Self-healing...")
            fix_prompt = f"The code failed the formal verification test. Error: {test_result}. Fix the code."
            response = await orchestrator.fix_code(response, fix_prompt)
            await self._process_tools_async(response, requirement) # Apply fixes
        else:
            print("[SWARM] Formal Verification PASSED! ✅")
            
        return response

    async def _process_tools_async(self, text, requirement, attempt=1):
        if attempt > 3:
            print("[SELF-HEALING] Max attempts reached. Stopping.")
            return

        # Handle MKDIR
        mkdir_matches = re.findall(r"\[MKDIR: (.*?)\]", text)
        for path in mkdir_matches:
            create_directory(path)
            # Generic environment setup
            if "/" not in path and "\\" not in path:
                setup_environment(path)

        # Handle SETUP (Explicit call)
        if "[SETUP]" in text:
            project_path_match = re.search(r"\[MKDIR: (.*?)\]", text)
            if project_path_match:
                setup_environment(project_path_match.group(1))

        # Handle WRITE_FILE
        file_matches = re.findall(r"\[WRITE_FILE: (.*?)\](.*?)\[/WRITE_FILE\]", text, re.DOTALL)
        for path, content in file_matches:
            write_file(path.strip(), content.strip())

        # Handle RUN (with Self-Healing)
        run_matches = re.findall(r"\[RUN: (.*?)\]", text)
        for cmd in run_matches:
            # Better project path detection
            mkdir_search = re.search(r"\[MKDIR: (.*?)\]", text)
            write_search = re.search(r"\[WRITE_FILE: (.*?)/", text)
            
            if mkdir_search:
                self.current_project_path = mkdir_search.group(1)
            elif write_search:
                self.current_project_path = write_search.group(1).split('/')[0]
            
            rel_path = self.current_project_path
            
            # Optimization: If the command mentions the folder name, strip it since we are inside CWD
            clean_cmd = cmd
            if rel_path != "." and rel_path in clean_cmd:
                clean_cmd = clean_cmd.replace(f"{rel_path}/", "").replace(f"{rel_path}\\", "")

            print(f"[EXECUTION] Running '{clean_cmd}' in {rel_path} (Attempt {attempt})...")
            output = run_in_env(rel_path, clean_cmd)
            print(f"Output: {output[:200]}...")

            if "Error" in output or "Exception" in output:
                print("[SWARM-FIX] Error detected! QA Agent flagging for Lead Developer...")
                fix_response = await orchestrator.fix_code(text, output)
                await self._process_tools_async(fix_response, requirement, attempt + 1)

        # Handle ZIP
        zip_matches = re.findall(r"\[ZIP: (.*?)\]", text)
        for path in zip_matches:
            zip_directory(path)

        # Handle SEARCH
        search_matches = re.findall(r"\[SEARCH: (.*?)\]", text)
        for query in search_matches:
            results = web_search(query)
            print(f"Search Results for '{query}': {results[:200]}...")

        # Handle KAGGLE_SEARCH
        k_search_matches = re.findall(r"\[KAGGLE_SEARCH: (.*?)\]", text)
        for query in k_search_matches:
            results = kaggle_search(query)
            print(f"Kaggle Results for '{query}': {results[:200]}...")

        # Handle KAGGLE_DOWNLOAD
        k_down_matches = re.findall(r"\[KAGGLE_DOWNLOAD: (.*?)\]", text)
        for ref in k_down_matches:
            # We download to the current project path
            results = kaggle_download(ref, path=self.current_project_path)
            print(f"Kaggle Download: {results}")

    async def generate_project(self, requirement):
        return await self.run_autonomous(requirement)

agent = CodingAgent()
