import os
import json
import csv
import re
from open_ai_module import client, chat_with_openai  # make sure this file is in the same folder

# Step 1: Run the prompt generation script
os.system("python task2b_create_jsons.py")  # assumes the script is named this way

# Step 2: Directories
input_dir = "prompts_task2b"
output_dir = "results_task2b"
os.makedirs(output_dir, exist_ok=True)

# Step 3: Helper function for versioned filenames
def get_next_versioned_filename(directory, base_name):
    i = 1
    while True:
        filename = f"{base_name}_{i:02}.csv"
        path = os.path.join(directory, filename)
        if not os.path.exists(path):
            return path
        i += 1

# Step 4: Iterate through each JSON prompt file
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
            match = re.search(r"\b(10|[0-9])\b", response)
            value = match.group(1) if match else "NA"
        except Exception as e:
            value = "NA"
        responses.append(value)

    # Step 5: Write to CSV
    headers = [f"{country_code} Q{i+1}" for i in range(len(user_prompts))]
    base_name = f"results_{country_code}_task2b"
    output_file = get_next_versioned_filename(output_dir, base_name)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerow(responses)

print("✅ All results saved in:", output_dir)
