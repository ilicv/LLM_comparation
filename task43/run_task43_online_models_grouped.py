# run_task43_online_models_grouped.py
# Processes attached prompts_* JSON files (EN, DE, SR).
# Sends ALL questions from each JSON in one prompt and expects a single line
# with N numbers (each 0-6) separated by spaces.

import os
import json
import csv
import time
import random
import re
from typing import List, Tuple

# ---- Provider modules (one model per provider) -------------------------------
import open_openai_module as oo        # chat_with_openai(oo.client, sys, user, model)
try:
    import open_mistral_module as mi   # make_client(), chat_with_mistral(client, sys, user, model)
except ImportError:
    import open_minstral_module as mi
import open_deepseek_module as ds      # load_api_key(), chat_with_deepseek(key, sys, user, model)
import open_grok_module as gx          # chat_with_grok(gx.client, sys, user, model)
import open_google_module as ge        # chat_with_gemini(sys, user, model), chat_with_gemma (sys, user, model)

# ---- Config ------------------------------------------------------------------
RESULTS_BASE = "results_task43_online"

# Exactly ONE model per provider (edit here if you want different ones)
OPENAI_MODEL   = "gpt-5-chat-latest"
MISTRAL_MODEL  = "mistral-large-latest"
DEEPSEEK_MODEL = "deepseek-chat"
#GROK_MODEL     = os.getenv("GROK_MODEL", "grok-4")
GROK_MODEL     = "grok-3-mini"
GEMINI_MODEL   = "gemini-2.5-pro"
GEMMA_MODEL  = "gemma-3-12b-it"

# Prompt files for Task 43 (DE, EN, SR)
PROMPT_DIR = "prompts_task43"
PROMPT_FILES = [
    os.path.join(PROMPT_DIR, "prompts_DE.json"),
    os.path.join(PROMPT_DIR, "prompts_EN.json"),
    os.path.join(PROMPT_DIR, "prompts_SR.json"),
]

PROVIDERS = {
    "openai": {
        "models": [OPENAI_MODEL],
        "call": lambda sys_msg, uq, model: oo.chat_with_openai(
            oo.client, sys_msg, uq, model=model, temperature=None
        ),
    },
    "mistral": {
        "init": lambda: mi.make_client(),
        "models": [MISTRAL_MODEL],
        "call": lambda sys_msg, uq, model, _client=None: mi.chat_with_mistral(_client, sys_msg, uq, model=model),
    },
    "deepseek": {
        "init": lambda: ds.load_api_key(),
        "models": [DEEPSEEK_MODEL],
        "call": lambda sys_msg, uq, model, _api_key=None: ds.chat_with_deepseek(_api_key, sys_msg, uq, model=model),
    },
    "grok": {
        "models": [GROK_MODEL],
        "call": lambda sys_msg, uq, model: gx.chat_with_grok(gx.client, sys_msg, uq, model=model),
    },
    "gemini": {
        "models": [GEMINI_MODEL],
        "call": lambda sys_msg, uq, model: ge.chat_with_gemini(sys_msg, uq, model=model),
    },
    "gemma": {
        "models": [GEMMA_MODEL],
        "call": lambda sys_msg, uq, model: ge.chat_with_gemma(sys_msg, uq, model=model),
    },
}

# ---- Helpers -----------------------------------------------------------------
def extract_grades_multi_1to5(text: str, n_expected: int) -> List[str]:
    """
    Extract the first n_expected standalone digits 1-5 from the response.
    Accepts spaces/commas/newlines; pads with 'ERR2' if fewer returned.
    """
    body = text.split("</think>")[-1] if "</think>" in text else text
    nums = re.findall(r"\b[1-5]\b", body)
    if len(nums) >= n_expected:
        return nums[:n_expected]
    return nums + ["ERR2"] * (n_expected - len(nums))

def next_index(dir_path: str, prefix: str) -> int:
    existing = [f for f in os.listdir(dir_path) if f.startswith(prefix) and f.endswith(".csv")]
    idxs = []
    for f in existing:
        m = re.search(r"_(\d+)\.csv$", f)
        if m:
            idxs.append(int(m.group(1)))
    return (max(idxs) + 1) if idxs else 1

def write_error_dump(err_path: str, sys_msg: str, uq: str, resp: str, note: str) -> None:
    with open(err_path, "a", encoding="utf-8") as outf:
        outf.write("---------\n")
        outf.write("SYSTEM:\n" + sys_msg + "\n\n")
        outf.write("USER (combined):\n" + uq + "\n\n")
        outf.write("-- RAW RESPONSE --\n" + (resp or "") + "\n")
        outf.write("-- NOTE --\n" + note + "\n")
        outf.write("---------\n")

def build_combined_prompt(sys_msg: str, questions: List[str]) -> Tuple[str, str]:
    """
    Keep the original system message but append strict output-format instruction.
    Combine all questions into one enumerated user prompt.
    (Task43 uses a 1-5 scale.)
    """
    n = len(questions)
    sys_multi = (
        sys_msg.strip()
        + f"\n\nINSTRUCTION: Answer ALL questions below in ONE line as exactly {n} numbers "
          "(each 1-5) separated by single spaces, in the same order. "
          "Do not add any text or punctuation."
    )
    user_multi = "\n".join(f"{i+1}) {q}" for i, q in enumerate(questions))
    return sys_multi, user_multi

def safe_model_dir_name(provider: str, model_name: str) -> str:
    return f"{RESULTS_BASE}_{provider}_{model_name.replace(':','_').replace('/','_')}"

# ---- Load & run --------------------------------------------------------------
for provider, cfg in PROVIDERS.items():
    # Optional init (client or API key)
    ctx = None
    if "init" in cfg and callable(cfg["init"]):
        try:
            ctx = cfg["init"]()
        except Exception as e:
            print(f"\n!! Skipping provider '{provider}' due to init error: {e}")
            continue

    for model_name in cfg["models"]:
        print(f"\n?? Running Task43 on provider: {provider}  model: {model_name}")
        model_dir = safe_model_dir_name(provider, model_name)
        os.makedirs(model_dir, exist_ok=True)

        for prompt_file in PROMPT_FILES:
            if not os.path.exists(prompt_file):
                print(f"!! Missing file: {prompt_file} (skipping)")
                continue

            # e.g., prompts_DE.json -> stem "DE"
            stem = os.path.splitext(os.path.basename(prompt_file))[0]
            stem = stem.split("_", 1)[-1] if "_" in stem else stem  # DE, SR, IE, UK

            with open(prompt_file, "r", encoding="utf-8") as pf:
                data = json.load(pf)

            # Paths for this file's results
            prefix = f"results_{stem}_task43_"
            file_index = next_index(model_dir, prefix)
            out_path = os.path.join(model_dir, f"{prefix}{file_index:02d}.csv")
            err_log = os.path.join(model_dir, f"{prefix}{file_index:02d}_ERRORS.txt")

            nums = []

            # -------- CASE A: old format -> {"System": "...", "User": ["...", "...", ...]} --------
            if isinstance(data, dict) and "System" in data and "User" in data:
                sys_msg = data["System"]
                questions = data["User"]
                headers = [f"Q{i+1}" for i in range(len(questions))]

                sys_multi, user_multi = build_combined_prompt(sys_msg, questions)
                print(f"?? [{provider}/{model_name}] {stem} Q1..Q{len(questions)}...", end=" ")
                try:
                    if provider in ("mistral", "deepseek"):
                        resp = cfg["call"](sys_multi, user_multi, model_name, ctx)
                    else:
                        resp = cfg["call"](sys_multi, user_multi, model_name)
                except Exception as e:
                    print(f"? error: {e}")
                    nums = ["ERR1"] * len(questions)
                    write_error_dump(err_log, sys_multi, user_multi, f"(Exception) {e}", "ERR1 for all")
                else:
                    nums = extract_grades_multi_1to5(resp, len(questions))
                    if any(x == "ERR2" for x in nums):
                        write_error_dump(err_log, sys_multi, user_multi, resp, "Missing numbers; filled ERR2")
                    print(" ".join(nums))

            # -------- CASE B: new format -> [{"System": "...", "User": "...", "sentence_id": "Q1"}, ...] --------
            elif isinstance(data, list):
                items = data
                headers = [(item.get("sentence_id") or f"Q{i+1}") for i, item in enumerate(items)]
                print(f"?? [{provider}/{model_name}] {stem} (iterating {len(items)} questions)...", end=" ")
                for i, item in enumerate(items, start=1):
                    sys_msg = (item.get("System") or "").strip()
                    user_q  = (item.get("User") or "").strip()
                    try:
                        if provider in ("mistral", "deepseek"):
                            resp = cfg["call"](sys_msg, user_q, model_name, ctx)
                        else:
                            resp = cfg["call"](sys_msg, user_q, model_name)
                    except Exception as e:
                        nums.append("ERR1")
                        write_error_dump(err_log, sys_msg, user_q, f"(Exception) {e}", f"ERR1 for item {i}")
                    else:
                        one = extract_grades_multi_1to5(resp, 1)[0]  # expect exactly one number
                        if one == "ERR2":
                            write_error_dump(err_log, sys_msg, user_q, resp, f"Missing number for item {i}; filled ERR2")
                        nums.append(one)
                print(" ".join(nums))

            # -------- Unknown format ------------------------------------------------------
            else:
                print(f"!! Unrecognized JSON structure in {prompt_file}")
                continue

            # Save CSV (one row per file) - unchanged
            with open(out_path, "w", newline="", encoding="utf-8") as outf:
                wr = csv.writer(outf)
                wr.writerow(headers)
                wr.writerow(nums)
            print(f" ? Saved: {out_path}")

            time.sleep(random.uniform(0.2, 0.5))

