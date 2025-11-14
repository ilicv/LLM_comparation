import os
import json
import csv
import time
import random
import re
from ollama_module import chat_with_ollama

PROMPT_DIR = "prompts_task1"
RESULTS_BASE = "results_task1_ollama"
# Hardcoded list of models to iterate over
MODELS = [
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
MODELS = [
    "deepseek-r1:32b",
]
'''



# Load all prompt JSONs once
prompt_files = [f for f in os.listdir(PROMPT_DIR) if f.endswith(".json")]

for model_name in MODELS:
    print(f"\n?? Running prompts on model: {model_name}")
    # Create a separate results directory per model
    model_dir = f"{RESULTS_BASE}_{model_name.replace(':', '_')}"
    os.makedirs(model_dir, exist_ok=True)

    for prompt_file in prompt_files:
        lang = prompt_file.split('_')[-1].split('.')[0]  # EN, DE, SR
        prompt_path = os.path.join(PROMPT_DIR, prompt_file)
        with open(prompt_path, "r", encoding="utf-8") as pf:
            groups = json.load(pf)

        # Build headers
        headers = []
        for grp in groups:
            target = grp["Target"]
            for i in range(len(grp["User"])):
                headers.append(f"{target} Q{i+1}")

        # Collect answers
        answers = []
        print(f"\n?? {lang} prompts on {model_name}")
        for grp in groups:
            sys_msg = grp["System"]
            for idx, uq in enumerate(grp["User"], start=1):
                header = f"{grp['Target']} Q{idx}"
                print(f"?? [{model_name}] {lang} {header}...", end=" ")
                try:
                    resp = chat_with_ollama(sys_msg, uq, model=model_name)
                except Exception as e:
                    print(f"? error: {e}")
                    answers.append("ERR1")
                    time.sleep(0.3)
                    continue

                # Strip reasoning and extract first digit 1-5
                body = resp.split("</think>")[-1] if "</think>" in resp else resp
                m = re.search(r"\b[1-5]\b", body)
                ans = m.group(0) if m else "ERR2"
                print(ans)
                if ans == 'ERR2':
                    #print (resp)
                    out_path_e = os.path.join(model_dir, f"results_{lang}_task1_{next_i:02d}_ERRORS.csv")
                    with open(out_path_e, "a", newline="", encoding="utf-8") as outf:
                        outf.write("---------\n")
                        outf.write(sys_msg+"\n")
                        outf.write(uq + "\n") 
                        outf.write("--\n")
                        outf.write(resp+"\n")
                        outf.write(ans+"\n")
                        outf.write("---------\n")

                answers.append(ans)
                time.sleep(random.uniform(0.2, 0.5))

        # Determine next file index
        existing = [f for f in os.listdir(model_dir)
                    if f.startswith(f"results_{lang}_task1_") and f.endswith(".csv")]
        idxs = [int(re.search(r"_(\d+)\.csv$", f).group(1)) for f in existing if re.search(r"_(\d+)\.csv$", f)]
        next_i = max(idxs, default=0) + 1

        # Save CSV
        out_path = os.path.join(model_dir, f"results_{lang}_task1_{next_i:02d}.csv")
        with open(out_path, "w", newline="", encoding="utf-8") as outf:
            wr = csv.writer(outf)
            wr.writerow(headers)
            wr.writerow(answers)
        print(f"? Saved: {out_path}")
