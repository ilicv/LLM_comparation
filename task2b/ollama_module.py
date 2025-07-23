import subprocess
import json

def chat_with_ollama(system_prompt, user_prompt, model="deepseek-r1:8b"):
    import ollama  # assumes `ollama` Python package is available

    # Join system + user into one message for simplicity
    full_prompt = f"{system_prompt.strip()}\n\n{user_prompt.strip()}"
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": full_prompt}],
        )
        return response['message']['content']
    except Exception as e:
        print(f"❌ Ollama call failed: {e}")
        return "ERR"