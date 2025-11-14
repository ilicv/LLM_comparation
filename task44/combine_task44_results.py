# combine_task44_results.py - include ollama/online folders + global upload CSV
import os
import csv
import re
from collections import defaultdict
from datetime import datetime

# Match per-test files like: results_DE_task44_01.csv or DE_task44_01.csv
pattern = re.compile(r"^(?:results_)?(EN|DE|SR)_task44_(\d+)\.csv$")

base_path = os.getcwd()

# --- derive model: everything after 'ollama' or 'online' in folder name
def derive_model_name(folder_name: str) -> str:
    """
    Examples:
      results_task44_online_openai_gpt-4o    -> openai_gpt-4o
      results_task44_ollama_gemma3_27b       -> gemma3_27b
    Fallback: last underscore-separated token.
    """
    m = re.search(r'(?:^|_)ollama[_-](.+)$', folder_name)
    if m:
        return 'offline_'+m.group(1)
    m = re.search(r'(?:^|_)online[_-](.+)$', folder_name)
    if m:
        return m.group(1)
    return folder_name.split("_")[-1]

# NEW: only scan Task 44 result folders (includes ollama/online/openai variants)
result_folders = [
    f for f in os.listdir(base_path)
    if os.path.isdir(f) and f.startswith("results_task44_")
]

# Global upload target
UPLOAD_DIR = os.path.join(base_path, "_upload")
os.makedirs(UPLOAD_DIR, exist_ok=True)
global_out = os.path.join(UPLOAD_DIR, "results_task44.csv")
global_header = ["datetime", "language", "model", "test number", "Q1", "Q2", "Q3", "Q4", "Q5"]
global_rows = []

for results_folder in result_folders:
    files_by_lang = defaultdict(list)

    # Collect matching files and group by language
    for file in os.listdir(results_folder):
        match = pattern.match(file)
        if match:
            lang, num = match.groups()
            files_by_lang[lang].append((int(num), file))

    # Process and combine per language
    for lang, files in files_by_lang.items():
        files.sort()
        output_file = os.path.join(results_folder, f"combined_{lang}_task44.csv")

        with open(output_file, "w", newline="", encoding="utf-8") as out_csv:
            writer = csv.writer(out_csv)
            header_written = False

            for test_num, file_name in files:
                file_path = os.path.join(results_folder, file_name)
                timestamp = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")

                with open(file_path, "r", encoding="utf-8") as in_csv:
                    reader = csv.reader(in_csv)
                    rows = list(reader)
                    if not rows:
                        continue

                    # Write per-language combined header once (preserve original file header)
                    if not header_written:
                        writer.writerow(["datetime", "test number"] + rows[0])
                        header_written = True

                    if len(rows) > 1:
                        # Write per-language combined row
                        writer.writerow([timestamp, f"{test_num:02d}"] + rows[1])

                        # Add to global upload accumulator
                        model_name = derive_model_name(results_folder)
                        answers = (rows[1] + [""] * 5)[:5]  # ensure exactly 5 answers
                        global_rows.append([timestamp, lang, model_name, f"{test_num:02d}"] + answers)

    if files_by_lang:
        print(f"✅ Combined task44 files created in: {results_folder}")
    else:
        print(f"⚠️ No matching task44 files found in: {results_folder}")

# Write the single _upload\results_task44.csv with all rows
with open(global_out, "w", newline="", encoding="utf-8") as gcsv:
    writer = csv.writer(gcsv)
    writer.writerow(global_header)
    writer.writerows(global_rows)

print(f"📤 Global upload written: {global_out}  (rows: {len(global_rows)})")
