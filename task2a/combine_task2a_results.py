# combine_task2a_results.py — adds global upload CSV for Task 2a
import os
import csv
import re
from collections import defaultdict
from datetime import datetime

# Base folder where all result subfolders are located
base_folder = "."

# Only process folders matching this pattern
subfolder_prefix = "results_task2a"

# Match filenames like: results_DE_task2a_01.csv (UK/IE/DE/SR)
file_pattern = re.compile(r"^results_(UK|IE|DE|SR)_task2a_(\d+)\.csv$")

# NEW: global accumulator + upload target
UPLOAD_DIR = os.path.join(base_folder, "_upload")
os.makedirs(UPLOAD_DIR, exist_ok=True)
global_path = os.path.join(UPLOAD_DIR, "results_task2a.csv")
global_header = ["datetime", "language", "model", "test number", "Q1", "Q2", "Q3", "Q4"]
global_rows = []

def derive_model_name(folder_name: str) -> str:
    """
    Return everything after 'ollama' or 'online' (underscore or hyphen),
    e.g. 'results_task2a_online_grouped_grok_grok-4' -> 'grok_grok-4'
         'results_task2a_ollama_qwen2-7b-instruct'   -> 'qwen2-7b-instruct'
    Falls back to the old behavior (last underscore token) if neither is found.
    """
    m = re.search(r'(?:^|_)ollama[_-](.+)$', folder_name)
    if m:
        return 'offiline_'+m.group(1)
    m = re.search(r'(?:^|_)online[_-](.+)$', folder_name)
    if m:
        return m.group(1)
    return folder_name.split("_")[-1]

# Iterate through all matching result folders
for folder_name in os.listdir(base_folder):
    if not folder_name.startswith(subfolder_prefix):
        continue

    folder_path = os.path.join(base_folder, folder_name)
    if not os.path.isdir(folder_path):
        continue

    print(f"🔄 Processing folder: {folder_name}")

    files_by_lang = defaultdict(list)

    # Group files by language
    for file in os.listdir(folder_path):
        match = file_pattern.match(file)
        if match:
            lang, num = match.groups()
            files_by_lang[lang].append((int(num), file))

    # Merge grouped files per-language (as before)
    for lang, files in files_by_lang.items():
        files.sort()  # Sort by test number
        output_file = os.path.join(folder_path, f"combined_{lang}_task2a.csv")

        with open(output_file, "w", newline="", encoding="utf-8") as out_csv:
            writer = csv.writer(out_csv)
            header_written = False

            for test_num, file_name in files:
                file_path = os.path.join(folder_path, file_name)
                # Get file's last modification datetime
                timestamp = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")

                print (file_path)
                with open(file_path, "r", encoding="utf-8") as in_csv:
                    reader = csv.reader(in_csv)
                    rows = list(reader)

                    if not rows:
                        continue

                    # Write per-language combined header once (keep your original structure)
                    if not header_written:
                        header = ["datetime", "test number"] + rows[0]
                        writer.writerow(header)
                        header_written = True

                    if len(rows) > 1:
                        # Write one row to the per-language combined CSV
                        writer.writerow([timestamp, f"{test_num:02d}"] + rows[1])

                        # ALSO append to the global upload accumulator
                        # Model = last underscore-separated token from the results folder name
                        model_name = derive_model_name(folder_name)
                        answers = rows[1][:4]  # Q1..Q4 only
                        # Pad to exactly 4 in case of malformed file
                        if len(answers) < 4:
                            answers = answers + [""] * (4 - len(answers))
                        global_rows.append([timestamp, lang, model_name, f"{test_num:02d}"] + answers)

        print(f"✅ {lang} combined file written to: {output_file}")

# Write the single _upload\results_task2a.csv with all rows
with open(global_path, "w", newline="", encoding="utf-8") as gcsv:
    writer = csv.writer(gcsv)
    writer.writerow(global_header)
    writer.writerows(global_rows)

print(f"📤 Global upload written: {global_path}  (rows: {len(global_rows)})")
print("🏁 All folders processed.")
