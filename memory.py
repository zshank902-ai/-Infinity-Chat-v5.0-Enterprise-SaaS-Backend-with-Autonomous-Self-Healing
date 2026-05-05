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
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                self.r = redis.Redis.from_url(redis_url, decode_responses=True, ssl_cert_reqs=None)
            else:
                self.r = redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                    password=os.getenv("REDIS_PASSWORD", None),
                    decode_responses=True
                )
            self.r.ping()
            self.enabled = True
            print("[MEMORY] Redis Connected. Global sync enabled.")
        except Exception as e:
            self.r = None
            print(f"[MEMORY] Redis unavailable: {e}. Using Local RAM fallback.")

    def save_chat(self, session_id, role, content):
        if self.enabled:
            history = self.get_history(session_id)
            history.append({"role": role, "content": content})
            self.r.set(f"chat:{session_id}", json.dumps(history), ex=3600*24) # 24h expiry
        
    def get_history(self, session_id):
        if self.enabled:
            data = self.r.get(f"chat:{session_id}")
            return json.loads(data) if data else []
        return []

    def is_rate_limited(self, key, limit=10, window=60):
        """Check if a key (like IP) has exceeded the rate limit."""
        if not self.enabled: return False # Fallback to no limit or local logic
        
        current = self.r.get(f"ratelimit:{key}")
        if current is not None and int(current) >= limit:
            return True
        
        pipe = self.r.pipeline()
        pipe.incr(f"ratelimit:{key}")
        pipe.expire(f"ratelimit:{key}", window)
        pipe.execute()
        return False

    def save_state(self, session_id, state_dict):
        """Persist the entire agent session state (God-Mode Persistence)."""
        if self.enabled:
            self.r.set(f"state:{session_id}", json.dumps(state_dict), ex=3600*12) # 12h persistence

    def get_state(self, session_id):
        """Retrieve the persisted agent session state."""
        if self.enabled:
            data = self.r.get(f"state:{session_id}")
            return json.loads(data) if data else None
        return None
    
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
redis_mem = RedisMemory()
vault = ProjectVault()
lessons = LessonVault()
