@echo off
setlocal enabledelayedexpansion

REM Create upload directory if it doesn't exist
if not exist "_upload" (
    mkdir "_upload"
)

REM Loop through all folders that start with "results"
for /d %%F in (results*) do (
    echo Processing folder: %%F

    REM Create corresponding folder inside _upload
    if not exist "_upload\%%F" (
        mkdir "_upload\%%F"
    )

    REM Copy combined_*.csv files only
    for %%C in (%%F\combined_*.csv) do (
        copy "%%C" "_upload\%%F\"
    )
)

echo ✅ All combined_ CSV files copied to _upload.
