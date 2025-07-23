import os
import json
import csv
import re
from ollama_module import chat_with_ollama  # Must be compatible with your Ollama interface

# Step 1: Generate the prompts
os.system("python task2b_create_jsons.py")

# Step 2: Directory setup
input_dir = "prompts_task2b"
models = [
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
models = [
     "deepseek-r1:32b",
]
'''




# Step 3: Create versioned output file helper
def get_next_versioned_filename(directory, base_name):
    i = 1
    while True:
        filename = f"{base_name}_{i:02}.csv"
        path = os.path.join(directory, filename)
        if not os.path.exists(path):
            return path
        i += 1

# Step 4: Process each model
for model_name in models:
    output_dir = f"results_task2b_ollama_{model_name.replace(':', '_')}"
    os.makedirs(output_dir, exist_ok=True)

    # Step 5: Loop over each prompt file
    for file_name in os.listdir(input_dir):
        if not file_name.endswith(".json"):
            continue

        country_code = file_name.replace("prompts_", "").replace(".json", "")
        filepath = os.path.join(input_dir, file_name)

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        system_prompt = data["System"]
        user_prompts = data["User"]
        responses = []

        for question in user_prompts:
            try:
                #response = chat_with_ollama(model_name, system_prompt, question)
                response = chat_with_ollama(system_prompt=system_prompt, user_prompt=question, model=model_name)
                match = re.search(r"\b(10|[0-9])\b", response)
                value = match.group(1) if match else "NA"
            except Exception as e:
                value = "ERR"
            responses.append(value)

        headers = [f"{country_code} Q{i+1}" for i in range(len(user_prompts))]
        base_name = f"results_{country_code}_task2b"
        output_file = get_next_versioned_filename(output_dir, base_name)

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerow(responses)

print("✅ All model runs completed and results saved.")
