import os
import json
import csv
import re
from ollama_module import chat_with_ollama  # assumes this handles Ollama LLM inference

# Define models to evaluate
OLLAMA_MODELS = [
    "llama3.2:3b",
    "mistral:latest",
    #"deepseek-coder:instruct",
    "deepseek-r1:8b",
    #"deepseek-r1:32b",
    #"deepseek-r1:70b",
    "gemma3:12b",
    "gemma3:27b",
    #"nomic-embed-text:latest",
]
'''
OLLAMA_MODELS = [
     "deepseek-r1:32b",
]
'''

# Input and output directories
input_dir = "prompts_task2a"
base_output_dir = "results_task2a_ollama"

# Utility for auto-incremented CSV filenames
def get_next_versioned_filename(directory, base_name):
    i = 1
    while True:
        filename = f"{base_name}_{i:02}.csv"
        path = os.path.join(directory, filename)
        if not os.path.exists(path):
            return path
        i += 1

# Loop through each model
for model_name in OLLAMA_MODELS:
    print(f"🚀 Processing with model: {model_name}")
    output_dir = f"{base_output_dir}_{model_name.replace(':', '_')}"
    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(input_dir):
        if not file_name.endswith(".json"):
            continue

        lang_code = file_name.replace("prompts_", "").replace(".json", "")
        input_path = os.path.join(input_dir, file_name)

        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        system_prompt = data["System"]
        user_prompts = data["User"]

        responses = []
        for question in user_prompts:
            try:
                reply = chat_with_ollama(system_prompt, question, model=model_name)
                match = re.search(r"\b([1-8])\b", reply)
                value = match.group(1) if match else "ERR"
            except Exception as e:
                print(f"⚠️ Error: {e}")
                value = "ERR"
            responses.append(value)

        headers = [f"Q{i+1}" for i in range(len(user_prompts))]
        base_filename = f"results_{lang_code}_task2a"
        csv_file_path = get_next_versioned_filename(output_dir, base_filename)

        with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerow(responses)

        print(f"✅ Saved: {csv_file_path}")
