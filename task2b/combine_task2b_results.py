import os
import csv
import re
from collections import defaultdict

# Base folder where all result subfolders are located
base_folder = "."

# Only process folders matching this pattern
subfolder_prefix = "results_task2b"
file_pattern = re.compile(r"^results_(UK|USA|DE|SR)_task2b_(\d+)\.csv$")

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

    # Merge grouped files
    for lang, files in files_by_lang.items():
        files.sort()  # Sort by test number
        output_file = os.path.join(folder_path, f"combined_{lang}_task2b.csv")

        with open(output_file, "w", newline="", encoding="utf-8") as out_csv:
            writer = csv.writer(out_csv)
            header_written = False

            for test_num, file_name in files:
                file_path = os.path.join(folder_path, file_name)

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

        print(f"✅ {lang} combined file written to: {output_file}")

print("🏁 All folders processed.")
