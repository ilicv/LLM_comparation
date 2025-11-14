# combine_task3b_results.py - include ollama & online; add global upload CSV
# Output schema: datetime, language, model, test number, Q1, Q2, Q3

import os
import csv
import re
from collections import defaultdict
from datetime import datetime

BASE_FOLDER = "."

# Include ALL Task3b folders (ollama, online, legacy, etc.)
SUBFOLDER_RX = re.compile(r"^results_task3b_")

# Accept BOTH: "DE_task3b_01.csv" and "results_DE_task3b_01.csv"
FILE_RX = re.compile(r"^(?:results_)?(UK|IE|DE|SR)_task3b_(\d+)\.csv$", re.IGNORECASE)

# Global upload target
UPLOAD_DIR = os.path.join(BASE_FOLDER, "_upload")
os.makedirs(UPLOAD_DIR, exist_ok=True)
GLOBAL_PATH = os.path.join(UPLOAD_DIR, "results_task3b.csv")
GLOBAL_HEADER = ["datetime", "language", "model", "test number", "Q1", "Q2", "Q3"]
global_rows = []

def derive_model_name(folder_name: str) -> str:
    """
    Model column = everything after 'ollama' or 'online' (underscore or hyphen).
    Examples:
      results_task3b_online_openai_gpt-4o   -> openai_gpt-4o
      results_task3b_ollama_gemma3_27b      -> gemma3_27b
    Fallback: last underscore-separated token.
    """
    m = re.search(r'(?:^|_)ollama[_-](.+)$', folder_name)
    if m:
        return 'offline_'+m.group(1)
    m = re.search(r'(?:^|_)online[_-](.+)$', folder_name)
    if m:
        return m.group(1)
    return folder_name.split("_")[-1]

def process_results_folder(folder_name: str):
    folder_path = os.path.join(BASE_FOLDER, folder_name)
    if not os.path.isdir(folder_path):
        return

    files_by_lang = defaultdict(list)

    # Collect files per language with flexible filename pattern
    for file in os.listdir(folder_path):
        m = FILE_RX.match(file)
        if not m:
            continue
        lang, num = m.groups()
        files_by_lang[lang.upper()].append((int(num), file))

    if not files_by_lang:
        print(f"⚠️  No Task3b files found in: {folder_name}")
        return

    model_name = derive_model_name(folder_name)

    # Combine per language and accumulate for global
    for lang, items in files_by_lang.items():
        items.sort()  # by test number
        out_path = os.path.join(folder_path, f"combined_{lang}_task3b.csv")
        header_written = False

        with open(out_path, "w", newline="", encoding="utf-8") as out_csv:
            writer = csv.writer(out_csv)

            for test_num, file_name in items:
                file_path = os.path.join(folder_path, file_name)
                ts = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")

                with open(file_path, "r", encoding="utf-8") as in_csv:
                    rows = list(csv.reader(in_csv))
                    if not rows:
                        continue

                    src_header = rows[0]  # keep original per-file header in combined_{LANG}
                    if not header_written:
                        writer.writerow(["datetime", "test number"] + src_header)
                        header_written = True

                    if len(rows) > 1:
                        data = rows[1]
                        # Write to per-language combined (zero-padded test number)
                        writer.writerow([ts, f"{test_num:02d}"] + data)

                        # Also add to global upload (Q1..Q3)
                        answers = (data + ["", "", ""])[:3]
                        global_rows.append([ts, lang, model_name, f"{test_num:02d}"] + answers)

        print(f"✅ {lang} combined file written: {out_path}")

def main():
    # Scan all folders that start with results_task3b_
    for folder_name in os.listdir(BASE_FOLDER):
        if SUBFOLDER_RX.match(folder_name) and os.path.isdir(folder_name):
            print(f"🔄 Processing folder: {folder_name}")
            process_results_folder(folder_name)

    # Write global upload CSV
    with open(GLOBAL_PATH, "w", newline="", encoding="utf-8") as gcsv:
        writer = csv.writer(gcsv)
        writer.writerow(GLOBAL_HEADER)
        writer.writerows(global_rows)

    print(f"📤 Global upload written: {GLOBAL_PATH}  (rows: {len(global_rows)})")
    print("🏁 All folders processed.")

if __name__ == "__main__":
    main()
