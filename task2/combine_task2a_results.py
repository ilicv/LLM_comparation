import os
import csv
import re
from collections import defaultdict

# Regex pattern to match relevant CSV files
pattern = re.compile(r"^results_(UK|USA|DE|SR)_task2a_(\d+)\.csv$")

# Iterate over all folders in current directory that start with "results"
base_path = os.getcwd()
all_result_folders = [f for f in os.listdir(base_path) if os.path.isdir(f) and f.startswith("results")]

for results_folder in all_result_folders:
    files_by_lang = defaultdict(list)

    for file in os.listdir(results_folder):
        match = pattern.match(file)
        if match:
            lang, num = match.groups()
            files_by_lang[lang].append((int(num), file))

    for lang, files in files_by_lang.items():
        files.sort()  # Sort by test number
        output_file = os.path.join(results_folder, f"combined_{lang}_task2a.csv")

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
        print(f"✅ Combined task2a files created in: {results_folder}")
    else:
        print(f"⚠️ No matching task2a files found in: {results_folder}")
