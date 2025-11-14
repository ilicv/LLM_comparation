# open_grok_module.py - xAI Grok (chat OK + robust model listing via REST)
# pip install xai-sdk requests

import os
from typing import Optional, Iterable, Any
import json
import requests

from xai_sdk import Client
from xai_sdk.chat import system, user as chat_user

KEY_FILE = "keys\\grok_API.txt"
XAI_API_BASE = os.getenv("XAI_API_BASE", "https://api.x.ai")
DEFAULT_MODEL = os.getenv("GROK_MODEL", "grok-4")

def load_api_key(path: str = KEY_FILE) -> str:
    if os.getenv("XAI_API_KEY"):
        return os.environ["XAI_API_KEY"].strip()
    if not os.path.exists(path):
        raise FileNotFoundError(f"API key file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        key = f.read().strip()
    if not key:
        raise ValueError(f"API key file '{path}' is empty.")
    return key

def make_client(api_key: Optional[str] = None) -> Client:
    api_key = api_key or load_api_key()
    return Client(api_key=api_key)

client = make_client()
_API_KEY = load_api_key()  # also used for REST fallback

# ----------------- Model listing (robust) -----------------

def _iter_models_blob(blob: Any) -> Iterable[Any]:
    if blob is None:
        return []
    if isinstance(blob, dict) and "data" in blob:
        return blob["data"]
    if hasattr(blob, "data"):
        return blob.data
    if isinstance(blob, (list, tuple)):
        return blob
    try:
        return list(blob)
    except Exception:
        return []

def list_available_models(client: Client):
    print("?? Available xAI Grok models:")
    # 1) Try common xai-sdk shapes
    try_order = [
        ("client.models.list()", lambda c: c.models.list()),
        ("client.models()",     lambda c: c.models()),
        ("client.models",       lambda c: c.models),
        ("client.list_models()",lambda c: c.list_models()),
    ]
    for _, call in try_order:
        try:
            blob = call(client)
            models = _iter_models_blob(blob)
            printed = False
            for m in models:
                name = getattr(m, "name", None) or getattr(m, "id", None) or str(m)
                print(f" - {name}")
                printed = True
            if printed:
                return
        except Exception:
            continue

    # 2) Fallback: direct REST call (OpenAI-compatible)
    try:
        url = f"{XAI_API_BASE.rstrip('/')}/v1/models"
        headers = {"Authorization": f"Bearer {_API_KEY}"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        payload = r.json()
        models = _iter_models_blob(payload)
        printed = False
        for m in models:
            # REST returns dicts with "id"
            name = m.get("id") if isinstance(m, dict) else str(m)
            print(f" - {name}")
            printed = True
        if printed:
            return
        print("(No models returned by REST endpoint)")
    except Exception as e:
        print(f"(Could not list models via known SDK methods or REST: {e})")
        print("Try known IDs like: grok-4, grok-3, grok-3-mini")

# ----------------- Chat (works in your run) -----------------

def chat_with_grok(client: Client,
                   system_prompt: str,
                   user_prompt: str,
                   model: str = DEFAULT_MODEL) -> str:
    """
    Single-turn chat using xAI SDK.
    Note: many xai-sdk builds don't accept temperature/top_p at sample-time.
          If your version supports gen-params at creation, add them to chat.create(...).
    """
    chat = client.chat.create(
        model=model,
        messages=[system(system_prompt)]
        # Example if your SDK supports it:
        # temperature=0.7, top_p=0.9
    )
    chat.append(chat_user(user_prompt))
    resp = chat.sample()  # no kwargs for many versions
    return getattr(resp, "content", None) or "(No content returned)"

# ----------------- Demo -----------------

if __name__ == "__main__":
    list_available_models(client)
    system_text = "You are a helpful assistant that answers concisely."
    user_text = "What is the capital of France?"
    print("\nGrok Response:\n", chat_with_grok(client, system_text, user_text))