import time
import asyncio
import re
import httpx
from groq import AsyncGroq
import google.generativeai as genai
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
        key = config.GROQ_KEYS[self.groq_key_index]
        self.groq_key_index = (self.groq_key_index + 1) % len(config.GROQ_KEYS)
        return AsyncGroq(api_key=key)

    def get_gemini_model(self):
        if not config.GEMINI_KEYS: return None
        key = config.GEMINI_KEYS[self.gemini_key_index]
        self.gemini_key_index = (self.gemini_key_index + 1) % len(config.GEMINI_KEYS)
        genai.configure(api_key=key)
        return genai.GenerativeModel('models/gemini-1.5-flash-latest')

    def get_deepseek_client(self):
        if not config.DEEPSEEK_KEYS: return None
        key = config.DEEPSEEK_KEYS[self.deepseek_key_index]
        self.deepseek_key_index = (self.deepseek_key_index + 1) % len(config.DEEPSEEK_KEYS)
        return AsyncOpenAI(api_key=key, base_url="https://api.deepseek.com")

    async def chat(self, prompt, provider=None, image_path=None):
        # TIER-BASED AUTO-SELECTION
        if not provider:
            if any(kw in prompt.lower() for kw in ["architect", "complex", "design", "plan"]):
                provider = "gemini" # Tier 1: Architect
            else:
                provider = "groq" # Tier 2: Developer/Fast

        try:
            if provider == "gemini":
                return await self._call_gemini(prompt, image_path)
            elif provider == "groq":
                return await self._call_groq(prompt)
            elif provider == "deepseek":
                return await self._call_deepseek(prompt)
            elif provider == "local":
                return await self._call_ollama(prompt)
            else:
                return await self._call_groq(prompt)
        except Exception as e:
            print(f"[ROUTER] Provider {provider} failed: {e}. Switching to Local Fallback...")
            return await self._call_ollama(prompt)

    async def _call_groq(self, prompt):
        client = self.get_groq_client()
        if not client: raise Exception("No Groq keys")
        resp = await client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        return resp.choices[0].message.content

    async def _call_gemini(self, prompt, image_path=None):
        model = self.get_gemini_model()
        if not model: raise Exception("No Gemini keys")
        loop = asyncio.get_event_loop()
        if image_path:
            import PIL.Image
            img = PIL.Image.open(image_path)
            response = await loop.run_in_executor(None, model.generate_content, [prompt, img])
        else:
            response = await loop.run_in_executor(None, model.generate_content, prompt)
        return response.text

    async def _call_deepseek(self, prompt):
        client = self.get_deepseek_client()
        if not client: raise Exception("No DeepSeek keys")
        resp = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

    async def _call_ollama(self, prompt):
        """Final Survival Layer: Local Llama 3 via Ollama."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.ollama_url,
                    json={"model": "llama3", "prompt": prompt, "stream": False},
                    timeout=120.0
                )
                return response.json().get("response", "Bhai, local brain is offline.")
        except Exception as e:
            return f"CRITICAL FAILURE: All providers and Local Fallback failed. {str(e)}"

router = APIRouter()
