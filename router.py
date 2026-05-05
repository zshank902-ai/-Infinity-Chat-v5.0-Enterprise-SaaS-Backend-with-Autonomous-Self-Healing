import time
import asyncio
import re
import httpx
from groq import AsyncGroq
from google import genai
from openai import AsyncOpenAI
from config import config

class APIRouter:
    def __init__(self):
        self.groq_key_index = 0
        self.gemini_key_index = 0
        self.deepseek_key_index = 0
        self.ollama_url = "http://localhost:11434/api/generate"
        
    def get_groq_client(self):
        if not config.GROQ_KEYS: return None
        # Auto-rotate key
        key = config.GROQ_KEYS[self.groq_key_index]
        self.groq_key_index = (self.groq_key_index + 1) % len(config.GROQ_KEYS)
        return AsyncGroq(api_key=key)

    def get_gemini_client(self):
        if not config.GEMINI_KEYS: return None
        # Auto-rotate key
        key = config.GEMINI_KEYS[self.gemini_key_index]
        self.gemini_key_index = (self.gemini_key_index + 1) % len(config.GEMINI_KEYS)
        return genai.Client(api_key=key)

    def get_deepseek_client(self):
        if not config.DEEPSEEK_KEYS: return None
        # Auto-rotate key
        key = config.DEEPSEEK_KEYS[self.deepseek_key_index]
        self.deepseek_key_index = (self.deepseek_key_index + 1) % len(config.DEEPSEEK_KEYS)
        return AsyncOpenAI(api_key=key, base_url="https://api.deepseek.com")

    async def chat(self, prompt, provider=None, image_path=None):
        # TIER-BASED AUTO-SELECTION (Groq is now Primary due to stability)
        if not provider:
            if any(kw in prompt.lower() for kw in ["architect", "complex", "design", "plan"]):
                provider = "groq" # Tier 1: Architect (Llama 3.3 70B)
            else:
                provider = "groq" # Tier 2: Developer/Fast

        # RETRY LOGIC (Max 2 retries)
        for attempt in range(3):
            try:
                if provider == "groq":
                    try:
                        return await self._call_groq(prompt, attempt)
                    except Exception as e:
                        if "429" in str(e) or "rate limit" in str(e).lower():
                            print(f"[ROUTER] Groq Rate Limited. Switching to Gemini Fallback...")
                            return await self._call_gemini(prompt, image_path)
                        raise e
                elif provider == "gemini":
                    return await self._call_gemini(prompt, image_path)
                elif provider == "deepseek":
                    return await self._call_deepseek(prompt)
                elif provider == "local":
                    return await self._call_ollama(prompt)
                else:
                    return await self._call_groq(prompt, attempt)
            except Exception as e:
                print(f"[ROUTER] Provider {provider} failed (Attempt {attempt+1}): {e}")
                if attempt == 2: # Last attempt
                    print(f"[ROUTER] All retries for {provider} failed. Switching to Local Fallback...")
                    return await self._call_ollama(prompt)
                await asyncio.sleep(2) # Wait before retry

    async def _call_groq(self, prompt, attempt=0):
        client = self.get_groq_client()
        if not client: raise Exception("No Groq keys")
        
        # Primary: Llama 3.1 8B (Instant) for High-Quota, Fallback: Llama 3.3 70B (Versatile)
        model_name = "llama-3.1-8b-instant" if attempt == 0 else "llama-3.3-70b-versatile"
        
        resp = await client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model_name
        )
        return {"response": resp.choices[0].message.content}

    async def _call_gemini(self, prompt, image_path=None):
        client = self.get_gemini_client()
        if not client: raise Exception("No Gemini keys")
        
        # Internal Gemini Fallback: Try Flash, then Pro
        models_to_try = ["gemini-1.5-flash", "gemini-pro"]
        last_err = None
        
        for model_id in models_to_try:
            try:
                loop = asyncio.get_event_loop()
                if image_path:
                    import PIL.Image
                    img = PIL.Image.open(image_path)
                    response = await loop.run_in_executor(
                        None, 
                        lambda: client.models.generate_content(model=model_id, contents=[prompt, img])
                    )
                else:
                    response = await loop.run_in_executor(
                        None, 
                        lambda: client.models.generate_content(model=model_id, contents=prompt)
                    )
                return {"response": response.text}
            except Exception as e:
                last_err = e
                print(f"[ROUTER] Gemini model {model_id} failed: {e}. Trying next...")
                continue
        
        raise last_err

    async def _call_deepseek(self, prompt):
        client = self.get_deepseek_client()
        if not client: raise Exception("No DeepSeek keys")
        resp = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"response": resp.choices[0].message.content}

    async def _call_ollama(self, prompt):
        """Final Survival Layer: Local Llama 3 via Ollama."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.ollama_url,
                    json={"model": "llama3", "prompt": prompt, "stream": False},
                    timeout=120.0
                )
                return {"response": response.json().get("response", "Local inference engine offline.")}
        except Exception as e:
            return f"CRITICAL FAILURE: All providers and Local Fallback failed. {str(e)}"

router = APIRouter()
