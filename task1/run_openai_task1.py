import os
import csv
import task1_create_jsons as task1  # corrected import
from open_ai_module import client, chat_with_openai


def get_next_versioned_filename(directory, base_name):
    i = 1
    while True:
        filename = f"{base_name}_{i:02}.csv"
        path = os.path.join(directory, filename)
        if not os.path.exists(path):
            return path
        i += 1

# Output directory
output_dir = "results_task1"
os.makedirs(output_dir, exist_ok=True)

# For each language
for lang_code in ["EN", "DE", "SR"]:
    prompts = task1.generate_prompts(task1.SUBJECT_all[lang_code], task1.TEMPLATES[lang_code], task1.lang_code)

    # Create headers: "women Q1", "women Q2", ...
    headers = []
    for prompt_set in prompts:
        subject = prompt_set["Target"]
        for i, _ in enumerate(prompt_set["User"]):
            headers.append(f"{subject} Q{i+1}")

    # Collect responses
    responses = []
    for prompt_set in prompts:
        system_msg = prompt_set["System"]
        for question in prompt_set["User"]:
            try:
                #reply = chat_with_openai(client, system_msg, question)
                reply = chat_with_openai(client, system_msg, question, model="gpt-4o")
                #reply = chat_with_openai(client, system_msg, question, model="gpt-4.1")
            except Exception as e:
                reply = f"Error: {str(e)}"
            responses.append(reply)

    # Save CSV
    base_name = f"results_{lang_code}_task1"
    csv_path = get_next_versioned_filename(output_dir, base_name)
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerow(responses)

print("✅ CSV files saved in 'results_task1/'")
