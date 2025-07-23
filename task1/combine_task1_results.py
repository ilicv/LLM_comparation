import os
import csv
import re
from collections import defaultdict

# Get all folders in the current directory that start with "results"
base_path = os.getcwd()
all_folders = [f for f in os.listdir(base_path) if os.path.isdir(f) and f.startswith("results")]

# Pattern to match expected result files
pattern = re.compile(r"^results_(EN|DE|SR)_task1_(\d+)\.csv$")

for results_folder in all_folders:
    files_by_lang = defaultdict(list)
    
    # Group CSV files by language
    for file in os.listdir(results_folder):
        match = pattern.match(file)
        if match:
            lang, num = match.groups()
            files_by_lang[lang].append((int(num), file))

    # Process and merge files by language
    for lang, files in files_by_lang.items():
        files.sort()  # Sort by test number
        output_file = os.path.join(results_folder, f"combined_{lang}_task1.csv")

        with open(output_file, "w", newline="", encoding="utf-8") as out_csv:
            writer = csv.writer(out_csv)
            header_written = False

            for test_num, file_name in files:
                file_path = os.path.join(results_folder, file_name)

                with open(file_path, "r", encoding="utf-8") as in_csv:
                    reader = csv.reader(in_csv)
                    rows = list(reader)

                    if not rows:
                        continue

                    if not header_written:
                        header = ["test number"] + rows[0]
                        writer.writerow(header)
                        header_written = True

                    if len(rows) > 1:
                        writer.writerow([f"{test_num:02d}"] + rows[1])

    if files_by_lang:
        print(f"✅ Combined results written for: {results_folder}")
    else:
        print(f"⚠️ No matching CSV files found in: {results_folder}")
