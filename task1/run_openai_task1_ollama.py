import os
import json
import csv
import time
import random
import re
from ollama_module import chat_with_ollama

PROMPT_DIR = "prompts_task1"
RESULTS_DIR = "results_task1_ollama"
MODEL_NAME = "deepseek-r1:8b"

# Ensure results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

# Process each prompt JSON (EN, DE, SR)
for prompt_file in os.listdir(PROMPT_DIR):
    if not prompt_file.endswith(".json"):
        continue

    # Determine language code (EN, DE, SR)
    lang_code = prompt_file.split('_')[-1].split('.')[0]
    prompt_path = os.path.join(PROMPT_DIR, prompt_file)

    # Load prompt list
    with open(prompt_path, 'r', encoding='utf-8') as pf:
        prompt_list = json.load(pf)

    # Prepare headers and responses
    headers = []
    responses = []

    print(f"\n🌐 Starting {lang_code} run...")

    # Iterate over each group of prompts
    for group in prompt_list:
        label = group['Target']
        system_msg = group['System']
        user_prompts = group['User']

        # For each question in this group
        for idx, user_q in enumerate(user_prompts, start=1):
            header = f"{label} Q{idx}"
            headers.append(header)
            print(f"🧠 Running {header}...")

            # Call Ollama
            try:
                resp = chat_with_ollama(system_msg, user_q)
                print(f"📥 Response: {resp}")
            except Exception as e:
                print(f"⚠️ Ollama error: {e}")
                resp = ""

            # Remove any reasoning block before extracting number
            if "</think>" in resp:
                resp_content = resp.split("</think>")[-1]
            else:
                resp_content = resp

            # Extract numeric answer 1-7 from the content
            # Use findall to capture any digit between 1 and 7
            digits = re.findall(r"[1-7]", resp_content)
            answer = digits[0] if digits else "ERR"
            responses.append(answer)

            # Throttle requests to avoid overload
            time.sleep(random.uniform(0.2, 0.5))

    # Determine next version number for the language
    existing = [f for f in os.listdir(RESULTS_DIR)
                if f.startswith(f"results_{lang_code}_task1_") and f.endswith(".csv")]
    nums = [int(re.search(r"_(\d+)\.csv$", f).group(1)) for f in existing if re.search(r"_(\d+)\.csv$", f)]
    next_idx = max(nums, default=0) + 1

    # Save CSV
    out_file = os.path.join(RESULTS_DIR, f"results_{lang_code}_task1_{next_idx:02d}.csv")
    with open(out_file, 'w', newline='', encoding='utf-8') as outf:
        writer = csv.writer(outf)
        writer.writerow(headers)
        writer.writerow(responses)

    print(f"✅ Saved: {out_file}")
