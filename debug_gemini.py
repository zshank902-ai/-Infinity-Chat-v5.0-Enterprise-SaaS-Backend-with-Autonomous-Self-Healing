import google.generativeai as genai
from backend.config import config

def debug_models():
    if not config.GEMINI_KEYS:
        print("No Gemini keys found.")
        return
    
    genai.configure(api_key=config.GEMINI_KEYS[0])
    print("Listing available models for your key...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_models()
