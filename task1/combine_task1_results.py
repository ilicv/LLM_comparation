# combine_task1_results.py — normalize DE/SR headers to English & build global CSV
import os
import csv
import re
from collections import defaultdict
from datetime import datetime

base_path = os.getcwd()
all_folders = [f for f in os.listdir(base_path) if os.path.isdir(f) and f.startswith("results")]

# Accept per-test files like: results_EN_task1_01.csv (with EN/DE/SR)
pattern = re.compile(r"^(?:results_)?(EN|DE|SR)_task1_(\d+)\.csv$")

# --- model column: everything after 'ollama' or 'online' in folder name
def derive_model_name(folder_name: str) -> str:
    m = re.search(r'(?:^|_)ollama[_-](.+)$', folder_name)
    if m:
        return 'offline_'+m.group(1)
    m = re.search(r'(?:^|_)online[_-](.+)$', folder_name)
    if m:
        return m.group(1)
    return folder_name.split("_")[-1]

# --- normalize non-English (and mojibake) group labels to English
PREFIX_MAP = {
    # English
    "women": "women",
    "men": "men",
    "refugees": "refugees",
    "asylum seekers": "asylum seekers",
    "economic migrants": "economic migrants",
    # Serbian (mojibake + proper)
    "Å¾ene": "women", "žene": "women",
    "muÅ¡karci": "men", "muškarci": "men",
    "izbeglice": "refugees",
    "traÅ¾ioci azila": "asylum seekers", "tražioci azila": "asylum seekers",
    "ekonomski migranti": "economic migrants",
    # German (mojibake + proper)
    "frauen": "women",
    "mÃ¤nner": "men", "männer": "men", "maenner": "men",
    "flÃ¼chtlinge": "refugees", "flüchtlinge": "refugees", "fluechtlinge": "refugees",
    "asylsuchende": "asylum seekers",
    "wirtschaftsmigranten": "economic migrants",
}

Q_COL_RE = re.compile(r"^\s*(.+?)\s*q\s*(\d+)\s*$", re.IGNORECASE)

def normalize_header_to_english(h: str) -> str:
    """Map 'Frauen Q1', 'Å¾ene Q1', etc. -> 'women Q1'. Leave 'datetime'/'test number' intact."""
    hl = h.strip().lower()
    if hl in ("datetime", "test number"):
        return hl  # keep canonical
    m = Q_COL_RE.match(hl)
    if not m:
        return hl  # unknown; pass through (won't be used)
    raw_prefix, qnum = m.groups()
    # squeeze internal spaces
    raw_prefix = " ".join(raw_prefix.split())
    eng_prefix = PREFIX_MAP.get(raw_prefix, raw_prefix)  # fallback: unchanged
    return f"{eng_prefix} Q{qnum}"

# --- Desired global header (Task 1, English)
subjects = ["women", "men", "refugees", "asylum seekers", "economic migrants"]
desired_cols = [f"{subj} Q{i}" for subj in subjects for i in range(1, 9)]
global_header = ["datetime", "language", "model", "test number"] + desired_cols

# Global accumulator
upload_dir = os.path.join(base_path, "_upload")
os.makedirs(upload_dir, exist_ok=True)
global_out = os.path.join(upload_dir, "results_task1.csv")
global_rows = []

for results_folder in all_folders:
    files_by_lang = defaultdict(list)

    # Group raw per-test CSVs by language
    for file in os.listdir(results_folder):
        match = pattern.match(file)
        if match:
            lang, num = match.groups()
            files_by_lang[lang].append((int(num), file))

    # Combine per language (keep your original behavior)
    for lang, files in files_by_lang.items():
        files.sort()
        output_file = os.path.join(results_folder, f"combined_{lang}_task1.csv")

        with open(output_file, "w", newline="", encoding="utf-8") as out_csv:
            writer = csv.writer(out_csv)
            header_written = False

            for test_num, file_name in files:
                file_path = os.path.join(results_folder, file_name)
                ts = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")

                with open(file_path, "r", encoding="utf-8") as in_csv:
                    reader = csv.reader(in_csv)
                    rows = list(reader)
                    if not rows:
                        continue

                    # Normalize the source header to English once
                    src_header = [normalize_header_to_english(h) for h in rows[0]]

                    # Write per-language combined header once (normalized to English)
                    if not header_written:
                        writer.writerow(["datetime", "test number"] + src_header)
                        header_written = True

                    if len(rows) > 1:
                        # Write to per-language combined as-is (normalized header already written)
                        writer.writerow([ts, f"{test_num:02d}"] + rows[1])

                        # ---- ALSO add to global upload (strict English order) ----
                        model_name = derive_model_name(results_folder)

                        # Build a lookup from normalized header -> value
                        data_row = rows[1]
                        lookup = {}
                        for idx, hnorm in enumerate(src_header):
                            lookup[hnorm] = data_row[idx] if idx < len(data_row) else ""

                        # Fill answers in required order; leave missing as ""
                        ordered_answers = [lookup.get(col, "") for col in desired_cols]

                        global_rows.append(
                            [ts, lang, model_name, f"{test_num:02d}"] + ordered_answers
                        )

    if files_by_lang:
        print(f"✅ Combined results written for: {results_folder}")
    else:
        print(f"⚠️ No matching CSV files found in: {results_folder}")

# Write single upload CSV with all rows across folders/languages
with open(global_out, "w", newline="", encoding="utf-8") as gcsv:
    writer = csv.writer(gcsv)
    writer.writerow(global_header)
    writer.writerows(global_rows)

print(f"📤 Global upload written: {global_out}  (rows: {len(global_rows)})")
