# combine_task3a_results.py - include ollama & online; add global upload CSV
import os
import csv
import re
from collections import defaultdict
from datetime import datetime

BASE = "."
FOLDER_RX = re.compile(r"^results_task3a_")  # include ollama / online / openai

# Accept BOTH: "EN_task3a_01.csv" and "results_EN_task3a_01.csv"
# NOTE: include EN as well as IE/DE/SR/UK
FILE_RX = re.compile(r"^(?:results_)?(UK|IE|DE|SR)_task3a_(\d+)\.csv$", re.IGNORECASE)

def derive_model_name(folder_name: str) -> str:
    """
    Return everything after 'ollama' or 'online' (underscore or hyphen).
    e.g. results_task3a_online_openai_gpt-4o -> openai_gpt-4o
         results_task3a_ollama_mistral_latest -> mistral_latest
    Fallback: last underscore-separated token (e.g. 'gpt-4.1').
    """
    m = re.search(r'(?:^|_)ollama[_-](.+)$', folder_name)
    if m:
        return 'offline_'+m.group(1)
    m = re.search(r'(?:^|_)online[_-](.+)$', folder_name)
    if m:
        return m.group(1)
    return folder_name.split("_")[-1]

def list_result_folders(root: str):
    return [
        d for d in os.listdir(root)
        if os.path.isdir(d) and FOLDER_RX.match(d)
    ]

def combine_folder(folder: str):
    files_by_lang = defaultdict(list)

    # Collect files per language
    for fn in os.listdir(folder):
        m = FILE_RX.match(fn)
        if not m:
            continue
        lang, num = m.groups()
        files_by_lang[lang.upper()].append((int(num), fn))

    if not files_by_lang:
        print(f"??  No Task3a files found in: {folder}")
        return None  # nothing to contribute to global

    per_folder_rows = []  # accumulate rows for global CSV
    per_folder_header = None  # remember header (Q1..Qn) for padding/truncation

    for lang, items in files_by_lang.items():
        items.sort()  # by test number
        out_path = os.path.join(folder, f"combined_{lang}_task3a.csv")
        header_written = False

        with open(out_path, "w", newline="", encoding="utf-8") as outf:
            wr = csv.writer(outf)

            for test_no, fn in items:
                path = os.path.join(folder, fn)
                ts = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")

                with open(path, "r", encoding="utf-8") as inf:
                    rows = list(csv.reader(inf))
                    if not rows:
                        continue

                    src_header = rows[0]  # typically ['Q1','Q2',...]
                    if per_folder_header is None:
                        per_folder_header = src_header[:]  # remember for global alignment

                    # Write header once in per-language combined file
                    if not header_written:
                        wr.writerow(["datetime", "test number"] + src_header)
                        header_written = True

                    if len(rows) > 1:
                        data = rows[1]
                        # write per-language combined
                        wr.writerow([ts, f"{test_no:02d}"] + data)

                        # store for global (we align later to the first header we see)
                        per_folder_rows.append({
                            "timestamp": ts,
                            "lang": lang,
                            "test_no": f"{test_no:02d}",
                            "data": data
                        })

        print(f"? {lang} combined file written: {out_path}")

    # Return what this folder contributes to the global CSV
    return per_folder_header, per_folder_rows

def main():
    folders = list_result_folders(BASE)
    if not folders:
        print("??  No folders named like 'results_task3a_*' found in current directory.")
        return

    # Global upload accumulator
    upload_dir = os.path.join(BASE, "_upload")
    os.makedirs(upload_dir, exist_ok=True)
    global_path = os.path.join(upload_dir, "results_task3a.csv")
    global_header = None
    global_rows = []

    for folder in folders:
        print(f"?? Processing folder: {folder}")
        out = combine_folder(folder)
        if not out:
            continue
        folder_header, folder_rows = out
        model_name = derive_model_name(folder)

        # Set/lock global header to first header encountered
        if global_header is None:
            # Build unified global header: datetime, language, model, test number, Q1..Qn
            global_header = ["datetime", "language", "model", "test number"] + folder_header

        # Align and append rows
        q_count = len(global_header) - 4
        for r in folder_rows:
            data = (r["data"] + [""] * q_count)[:q_count]  # pad/truncate
            global_rows.append([r["timestamp"], r["lang"], model_name, r["test_no"]] + data)

    # Write the single global CSV if we gathered anything
    if global_header is not None:
        with open(global_path, "w", newline="", encoding="utf-8") as gcsv:
            wr = csv.writer(gcsv)
            wr.writerow(global_header)
            wr.writerows(global_rows)
        print(f"?? Global upload written: {global_path}  (rows: {len(global_rows)})")
    else:
        print("??  No Task3a rows found to write into the global CSV.")

if __name__ == "__main__":
    main()
