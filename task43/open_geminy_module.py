# open_geminy_module.py  (Gemini version)
# Requires: pip install google-generativeai

import os
import sys
from typing import Optional

try:
    import google.generativeai as genai
except ImportError:
    raise SystemExit("Missing dependency: run `pip install google-generativeai`")

# --- API key & client ---------------------------------------------------------

KEY_FILE = "keys\\gemini_API.txt"  # put your Gemini API key in this file (single line)

def load_api_key(path: str = KEY_FILE) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"API key file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        key = f.read().strip()
    if not key:
        raise ValueError(f"API key file '{path}' is empty.")
    return key

def configure_gemini(api_key: Optional[str] = None):
    api_key = api_key or load_api_key()
    genai.configure(api_key=api_key)

# --- Model helpers ------------------------------------------------------------

def list_available_models():
    """
    Print public Gemini model IDs you can call with the SDK.
    (Note: availability depends on your account/region.)
    """
    configure_gemini()
    print("?? Available Gemini models:")
    for m in genai.list_models():
        # We filter for models that support text generation
        if "generateContent" in m.supported_generation_methods:
            print(f" - {m.name}")

# --- Chat (system + user) -----------------------------------------------------

def chat_with_gemini(system_prompt: str,
                     user_prompt: str,
                     model: str = "gemini-1.5-pro",
                     temperature: float = 0.7) -> str:
    """
    Sends a single-turn prompt to Gemini, using 'system_prompt' as
    the system instruction. For multi-turn, switch to the 'start_chat'
    pattern with history (see notes below).
    """
    configure_gemini()

    gm = genai.GenerativeModel(
        model,
        system_instruction=system_prompt
    )

    resp = gm.generate_content(
        user_prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature
        )
    )

    # Handle safety blocks or empty responses gracefully
    if not resp or not getattr(resp, "text", None):
        return "(No content returned)"
    return resp.text

# --- Demo ---------------------------------------------------------------------

if __name__ == "__main__":
    # Step 1: List models
    try:
        list_available_models()
    except Exception as e:
        print(f"Warning: could not list models ({e})", file=sys.stderr)

    # Example input
    system_text = "You are a helpful assistant that answers concisely."
    user_text = "What is the capital of France?"

    try:
        result = chat_with_gemini(system_text, user_text)
        print("Gemini Response:\n", result)
    except Exception as e:
        print(f"Error calling Gemini: {e}", file=sys.stderr)
