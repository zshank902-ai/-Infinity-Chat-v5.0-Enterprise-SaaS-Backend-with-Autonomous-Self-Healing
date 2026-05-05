import json
import os
import time
from pathlib import Path

MEMORY_FILE = Path("./data/memory.json")


class RedisMemory:
    """Enterprise-grade distributed memory (Global Sync)."""
    def __init__(self):
        self.enabled = False
        try:
            import redis
            # Using environment variables for Upstash/Railway Redis
            self.r = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                password=os.getenv("REDIS_PASSWORD", None),
                decode_responses=True
            )
            self.r.ping()
            self.enabled = True
            print("[MEMORY] Redis Connected. Global sync enabled.")
        except:
            self.r = None
            print("[MEMORY] Redis unavailable. Using Local RAM fallback.")

    def save_chat(self, session_id, role, content):
        if self.enabled:
            history = self.get_history(session_id)
            history.append({"role": role, "content": content})
            self.r.set(f"chat:{session_id}", json.dumps(history))
        
    def get_history(self, session_id):
        if self.enabled:
            data = self.r.get(f"chat:{session_id}")
            return json.loads(data) if data else []
        return []
    
class Memory:
    def __init__(self):
        self.history = self._load_memory()

    def _load_memory(self):
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"sessions": {}}

    def save_chat(self, session_id, role, content):
        if session_id not in self.history["sessions"]:
            self.history["sessions"][session_id] = []
        
        self.history["sessions"][session_id].append({
            "role": role,
            "content": content
        })
        self._persist()

    def get_history(self, session_id):
        return self.history["sessions"].get(session_id, [])

    def _persist(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4)

class ProjectVault:
    def __init__(self):
        self.vault_path = Path("./memory/vault")

        self.vault_path.mkdir(parents=True, exist_ok=True)

    def save_project_card(self, project_name, summary):
        card_path = self.vault_path / f"{project_name}.json"
        card_data = {
            "project_name": project_name,
            "timestamp": time.time(),
            "summary": summary
        }
        with open(card_path, "w") as f:
            json.dump(card_data, f, indent=4)
        return f"Project card saved for {project_name}"

    def get_all_summaries(self):
        summaries = []
        for file in self.vault_path.glob("*.json"):
            with open(file, "r") as f:
                summaries.append(json.load(f))
        return summaries

class LessonVault:
    def __init__(self):
        self.lessons_path = Path("./memory/lessons")

        self.lessons_path.mkdir(parents=True, exist_ok=True)

    def save_lesson(self, project_name, lessons):
        lesson_file = self.lessons_path / f"{project_name}_lessons.txt"
        with open(lesson_file, "w", encoding="utf-8") as f:
            f.write(f"PROJECT: {project_name}\nTIMESTAMP: {time.time()}\n\nLESSONS:\n{lessons}")
        return f"Lesson saved for {project_name}"

    def add_lesson(self, content):
        # Auto-name lesson based on timestamp
        ts = int(time.time())
        lesson_file = self.lessons_path / f"lesson_{ts}.txt"
        with open(lesson_file, "w", encoding="utf-8") as f:
            f.write(f"TIMESTAMP: {ts}\n\n{content}")
        return f"Lesson added: {ts}"

    def get_all_lessons(self):
        lessons = ""
        for file in self.lessons_path.glob("*.txt"):
            with open(file, "r", encoding="utf-8") as f:
                lessons += f"\n--- PAST LESSON ---\n{f.read()}\n"
        return lessons

memory = Memory()
vault = ProjectVault()
lessons = LessonVault()
