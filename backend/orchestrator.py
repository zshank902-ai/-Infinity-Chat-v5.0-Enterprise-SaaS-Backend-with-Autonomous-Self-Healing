from router import router

class Orchestrator:
    def __init__(self):
        self.consultant = "gemini"   # User Interview & Requirements
        self.architect = "gemini"    # Planning & Design
        self.developer = "gemini"    # Coding
        self.security = "groq"       # Security Audit (Fast)
        self.tester = "groq"         # Bug Finding (Fast)

    async def interview_user(self, requirement):
        prompt = f"Role: Witty Product Manager\nTask: The user wants to build: {requirement}. Ask 3-5 concise, targeted questions to clarify the project scope.\nNote: Be friendly, use a bit of developer humor/banter, and communicate in the user's language."
        return await router.chat(prompt, provider=self.consultant)

    async def analyze_requirement(self, requirement, history):
        prompt = f"Role: Strategic Consultant\nTask: Analyze this requirement: {requirement}\nHistory: {history}\nReturn a JSON with: 'complexity' (Low/Medium/High), 'confidence_score' (1-100), and 'missing_info' (list of things to ask)."
        response = await router.chat(prompt, provider=self.consultant)
        return response

    async def generate_blueprint(self, requirement, interview_data):
        prompt = f"Role: Senior Architect\nTask: Create a detailed technical blueprint.\nRequirement: {requirement}\nInterview: {interview_data}\nNote: If multi-service, ALWAYS include an API Gateway and Docker-compose structure. Present in user language, technicals in English."
        return await router.chat(prompt, provider=self.architect)

    async def architect_plan(self, requirement):
        prompt = f"Role: Senior Architect\nTask: Design the BEST architecture for: {requirement}. For microservices, provide Dockerfiles for each service and a central docker-compose.yml."
        return await router.chat(prompt, provider=self.architect)

    async def security_audit(self, code):
        prompt = f"Role: Cybersecurity Expert\nTask: Audit this code for vulnerabilities (SQL Injection, XSS, etc.). Respond with 'SECURE' or a list of issues:\n\n{code}"
        return await router.chat(prompt, provider=self.security)

    async def qa_review(self, code, requirement):
        prompt = f"Role: Senior QA Engineer\nTask: Review this code against the requirement: {requirement}. Does it meet all criteria? List any bugs."
        return await router.chat(prompt, provider=self.tester)

    async def formal_verification(self, requirement, code):
        """Generates a standalone test script to verify functional correctness."""
        prompt = f"Role: QA Engineer\nTask: Generate a standalone Python test script to verify if this code meets the requirement: {requirement}.\n\nCode to Test:\n{code}\n\nThe script must use assertions and exit with code 0 on success. ONLY RETURN THE CODE."
        return await router.chat(prompt, provider=self.tester)

    async def code_implementation(self, requirement, plan, file_path):
        prompt = f"Role: Senior Full-Stack Developer\nTask: Implement {file_path} based on this plan: {plan}. Requirement: {requirement}."
        return await router.chat(prompt, provider=self.developer)

    async def fix_code(self, code, error_or_feedback):
        prompt = f"Role: Lead Developer\nTask: Fix the following code based on this error/feedback: {error_or_feedback}\n\nCode:\n{code}"
        return await router.chat(prompt, provider=self.developer)

    async def summarize_project(self, requirement, file_list):
        prompt = f"Role: Technical Writer\nTask: Create a concise JSON-formatted summary of this project.\nRequirement: {requirement}\nFiles: {file_list}\nInclude: Tech stack, core features, and main endpoints."
        return await router.chat(prompt, provider=self.architect)

    async def analyze_data_science_patterns(self, dataset_info, sample_data):
        prompt = f"Role: Senior Data Scientist\nTask: Analyze this Kaggle dataset info and sample data.\nDataset: {dataset_info}\nSample: {sample_data}\nProvide: 1. Best preprocessing steps. 2. Ideal ML models. 3. Key insights for the project."
        return await router.chat(prompt, provider=self.architect)

    async def reflect_on_project(self, requirement, logs):
        prompt = f"Role: Senior Quality Auditor\nTask: Reflect on the project build for: {requirement}.\nExecution Logs: {logs}\nIdentify: 1. Top 3 technical lessons learned. 2. Mistakes to avoid next time. 3. Best library used."
        return await router.chat(prompt, provider=self.tester)

orchestrator = Orchestrator()
