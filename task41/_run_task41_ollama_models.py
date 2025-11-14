import os
import json
import csv
import re
from datetime import datetime
from ollama_module import chat_with_ollama

PROMPT_FOLDER = "prompts_taskba"

# List of models to run
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

def get_output_filename(language, model_name):
    result_folder = f"results_task3b_ollama_{model_name.replace(':', '_')}"
    os.makedirs(result_folder, exist_ok=True)
    base_name = f"{language}_task3b"
    version = 1
    while os.path.exists(os.path.join(result_folder, f"{base_name}_{version:02d}.csv")):
        version += 1
    return os.path.join(result_folder, f"{base_name}_{version:02d}.csv")

def detect_language(filename):
    for lang in ["EN", "IE", "DE", "SR"]:
        if filename.endswith(f"{lang}.json"):
            return lang
    return "UNKNOWN"

def extract_numeric_answer(text):
    """Extract the first number from 0 to 9 (or 10) from the response"""
    match = re.search(r"\b([0-9]|10)\b", text)
    return match.group(1) if match else "NA"

def run_task3b_for_model(model_name):
    print(f"?? Running prompts for model: {model_name}")
    results_by_language = {}
    headers_by_language = {}

    filenames = sorted(os.listdir(PROMPT_FOLDER))

    for filename in filenames:
        if filename.endswith(".json"):
            lang = detect_language(filename)
            filepath = os.path.join(PROMPT_FOLDER, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            system_prompt = data["System"]
            user_prompts = data["User"]
            row = []

            for i, question in enumerate(user_prompts, start=1):
                print(f"?? {filename} | Q{i}: {question[:60]}...")
                response = chat_with_ollama(system_prompt, question, model=model_name)
                numeric = extract_numeric_answer(response)
                row.append(numeric)

            results_by_language.setdefault(lang, []).append(row)
            headers_by_language.setdefault(lang, []).extend(
                [f"{filename.replace('.json','')} Q{i+1}" for i in range(len(user_prompts))]
            )

    for lang, rows in results_by_language.items():
        output_file = get_output_filename(lang, model_name)
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers_by_language[lang])
            for row in rows:
                writer.writerow(row)
        print(f"? {lang} results saved to: {output_file}")

if __name__ == "__main__":
    for model in OLLAMA_MODELS:
        run_task3b_for_model(model)
