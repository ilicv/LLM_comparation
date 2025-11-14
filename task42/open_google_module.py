# open_google_module.py  (Gemini and Gemma version)
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
    Single-turn call to Gemini with a robust text extractor that never raises
    when the response has empty/blocked candidates.
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
            # You can also set response_mime_type="text/plain" here in newer SDKs
        )
    )

    # --- Safe extractor (never throws when .text is unavailable) ---
    def _resp_to_text(r):
        # Try the quick accessor, but swallow its internal errors
        try:
            t = r.text
            if t:
                return t
        except Exception:
            pass
        # Fallback: stitch together any text parts from the first candidate
        try:
            if getattr(r, "candidates", None):
                cand = r.candidates[0]
                content = getattr(cand, "content", None)
                parts = getattr(content, "parts", None) if content else None
                if parts:
                    chunks = []
                    for p in parts:
                        t = getattr(p, "text", None)
                        if t:
                            chunks.append(t)
                    if chunks:
                        return "\n".join(chunks)
        except Exception:
            pass
        return ""

    text = _resp_to_text(resp)
    return text if text else "(No content returned)"

def chat_with_gemma(system_prompt: str,
                    user_prompt: str,
                    model: str = "gemma-3-12b-it",
                    temperature: float = 0.7) -> str:
    """
    Single-turn call to Gemma model.
    IMPORTANT: Gemma models do not support system_instruction.
    Therefore we concatenate system and user prompts into one text input.
    """
    configure_gemini()

    gm = genai.GenerativeModel(model)

    # Concatenate system + user prompts into a single input
    full_prompt = f"{system_prompt.strip()}\n\n{user_prompt.strip()}"

    resp = gm.generate_content(
        full_prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
            response_mime_type="text/plain"
        )
    )

    # --- Safe extractor (same as in chat_with_gemini) ---
    def _resp_to_text(r):
        try:
            t = r.text
            if t:
                return t
        except Exception:
            pass
        try:
            if getattr(r, "candidates", None):
                cand = r.candidates[0]
                content = getattr(cand, "content", None)
                parts = getattr(content, "parts", None) if content else None
                if parts:
                    chunks = []
                    for p in parts:
                        t = getattr(p, "text", None)
                        if t:
                            chunks.append(t)
                    if chunks:
                        return "\n".join(chunks)
        except Exception:
            pass
        return ""

    text = _resp_to_text(resp)
    return text if text else "(No content returned)"

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
