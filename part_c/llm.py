"""Tiny LLM wrapper. Uses Gemini when GEMINI_API_KEY is set, otherwise returns the fallback."""
import os
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
def llm(prompt, fallback=None):
    key = os.getenv("GEMINI_API_KEY")
    if not key: return fallback
    try:
        import httpx
        r = httpx.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                       params={"key": key}, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
        r.raise_for_status(); return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return fallback
