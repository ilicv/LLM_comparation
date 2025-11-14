# open_minstral_module.py
"""
Mistral API client using mistralai v1 (like your t.py).
- Reads API key from 'minstral_API_key.txt' (one line with the key).
- Lists models.
- Runs a simple chat completion.
- Adds a small CLI for convenience.
"""

import os
import argparse
from typing import List, Dict, Any
from mistralai import Mistral

KEY_FILE = "keys\\mistral_API.txt"


# --- API key & client ---------------------------------------------------------

def load_api_key(path: str = KEY_FILE) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"API key file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        key = f.read().strip()
    if not key:
        raise ValueError(f"API key file '{path}' is empty.")
    return key


def make_client() -> Mistral:
    # If you want, you can pass server_url="https://api.mistral.ai"
    return Mistral(api_key=load_api_key())


# --- API wrappers -------------------------------------------------------------

def list_available_models(client: Mistral) -> None:
    """List available Mistral models via v1 SDK."""
    try:
        res = client.models.list()
        data = getattr(res, "data", res)
        print("?? Available Mistral models:")
        for m in data:
            print(f" - {getattr(m, 'id', str(m))}")
    except Exception as e:
        print(f"?? Could not list models: {e}")


def chat_with_mistral(
    client: Mistral,
    system_prompt: str,
    user_prompt: str,
    model: str = "mistral-large-latest",
    temperature: float = 0.7,
) -> str:
    """Chat completion using the same pattern as t.py (v1)."""
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": system_prompt.strip()} if system_prompt else None,
        {"role": "user", "content": user_prompt.strip()},
    ]
    # remove possible None if system_prompt is empty
    messages = [m for m in messages if m is not None]

    resp = client.chat.complete(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=False,
    )
    return resp.choices[0].message.content


# --- CLI ----------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Mistral chat via mistralai v1 SDK")
    p.add_argument("--list", action="store_true", help="List models and exit")
    p.add_argument("--model", default="mistral-large-latest", help="Model id")
    p.add_argument("--temp", type=float, default=0.7, help="Temperature")
    p.add_argument("--system", default="You are a helpful assistant that answers concisely.",
                   help="System prompt")
    p.add_argument("--user", default="What is the capital of France?",
                   help="User prompt")
    return p.parse_args()


# --- Main ---------------------------------------------------------------------

if __name__ == "__main__":
    args = parse_args()
    client = make_client()

    if args.list:
        list_available_models(client)
    else:
        out = chat_with_mistral(
            client,
            system_prompt=args.system,
            user_prompt=args.user,
            model=args.model,
            temperature=args.temp,
        )
        print("\nMistral Response:\n", out)
