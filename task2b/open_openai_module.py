import openai
import os   
KEY_FILE = "keys\\openai_API.txt"


# --- API key & client ---------------------------------------------------------

def load_api_key(path: str = KEY_FILE) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"API key file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        key = f.read().strip()
    if not key:
        raise ValueError(f"API key file '{path}' is empty.")
    return key

client = openai.OpenAI(api_key=load_api_key())

def list_available_models(client):
    models = client.models.list()
    print("📦 Available OpenAI models:")
    for model in models.data:
        print(f" - {model.id}")


#def chat_with_openai(client, system_prompt: str, user_prompt: str, model="gpt-4o"):
def chat_with_openai(client, system_prompt: str, user_prompt: str, model="gpt-4.1"):

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content



if __name__ == "__main__":
    # Step 1: List models
    list_available_models(client)

    # Example input
    system_text = "You are a helpful assistant that answers concisely."
    user_text = "What is the capital of France?"

    result = chat_with_openai(client, system_text, user_text)
    print("OpenAI Response:\n", result)