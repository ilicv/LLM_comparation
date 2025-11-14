# open_deepseek_module.py
"""
DeepSeek API client via HTTP only (no OpenAI SDK).
- Reads API key from 'deepseek_API.txt' (one line).
- Lists models (GET /v1/models).
- Sends chat completions (POST /v1/chat/completions).
- CLI:
    --list
    --model deepseek-chat|deepseek-reasoner
    --system "..."
    --user "..."
    --temp 0.7
"""
import os
import json
import argparse
from typing import Dict, Any, List
import httpx

KEY_FILE = "keys\\deepseek_API.txt"
BASE_URL = "https://api.deepseek.com/v1"


def load_api_key(path: str = KEY_FILE) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"API key file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        key = f.read().strip()
    if not key:
        raise ValueError(f"API key file '{path}' is empty.")
    return key


def _headers(api_key: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def list_available_models(api_key: str) -> None:
    with httpx.Client() as client:
        r = client.get(f"{BASE_URL}/models", headers=_headers(api_key), timeout=30.0)
        r.raise_for_status()
        data = r.json()
        items = data.get("data", data)
        print("?? Available DeepSeek models:")
        for m in items:
            print(f" - {m.get('id', m)}")


def chat_with_deepseek(
    api_key: str,
    system_prompt: str,
    user_prompt: str,
    model: str = "deepseek-chat",
    temperature: float = 0.7,
) -> str:
    messages: List[Dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt.strip()})
    messages.append({"role": "user", "content": user_prompt.strip()})

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    with httpx.Client() as client:
        r = client.post(
            f"{BASE_URL}/chat/completions",
            headers=_headers(api_key),
            content=json.dumps(payload),
            timeout=60.0,
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]


def parse_args():
    p = argparse.ArgumentParser(description="DeepSeek chat via HTTP (no SDK)")
    p.add_argument("--list", action="store_true", help="List available models and exit")
    p.add_argument("--model", default="deepseek-chat", help="Model id")
    p.add_argument("--temp", type=float, default=0.7, help="Sampling temperature")
    p.add_argument(
        "--system",
        default="You are a helpful assistant that answers concisely.",
        help="System prompt",
    )
    p.add_argument("--user", default="What is the capital of France?", help="User prompt")
    return p.parse_args()


if __name__ == "__main__":
    key = load_api_key()
    args = parse_args()

    if args.list:
        try:
            list_available_models(key)
        except httpx.HTTPStatusError as e:
            print(f"? HTTP {e.response.status_code}: {e.response.text}")
            raise
    else:
        try:
            out = chat_with_deepseek(
                key,
                system_prompt=args.system,
                user_prompt=args.user,
                model=args.model,
                temperature=args.temp,
            )
            print("\nDeepSeek Response:\n", out)
        except httpx.HTTPStatusError as e:
            print(f"? HTTP {e.response.status_code}: {e.response.text}")
            raise
