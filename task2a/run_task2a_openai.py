import os
import json
import csv
import re
from open_ai_module import client, chat_with_openai  # assumes open_ai_module.py is in the same directory

# Directories
input_dir = "prompts_task2a"             # JSON files created by task2a_create_jsons.py
output_dir = "results_task2a"
os.makedirs(output_dir, exist_ok=True)

# Helper to auto-version result files
def get_next_versioned_filename(directory, base_name):
    i = 1
    while True:
        filename = f"{base_name}_{i:02}.csv"
        path = os.path.join(directory, filename)
        if not os.path.exists(path):
            return path
        i += 1

# Process each country file
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
            response = chat_with_openai(client, system_prompt, question)
            match = re.search(r"\b([0-7])\b", response)
            value = match.group(1) if match else "NA"
        except Exception as e:
            value = "NA"
        responses.append(value)

    # Save to CSV in one row
    headers = [f"Q{i+1}" for i in range(len(user_prompts))]
    base_name = f"results_{country_code}_task2a"
    output_file = get_next_versioned_filename(output_dir, base_name)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(responses)

print("✅ Results saved to:", output_dir)
