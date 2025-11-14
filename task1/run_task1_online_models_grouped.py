# run_task1_online_models.py
# ONE model per provider; asks ALL questions in a category in a single prompt.

import os
import json
import csv
import time
import random
import re
from typing import List

# ---- Import provider modules -------------------------------------------------
import open_openai_module as oo        # chat_with_openai(oo.client, sys, user, model)
try:
    import open_mistral_module as mi   # make_client(), chat_with_mistral(client, sys, user, model)
except ImportError:
    import open_minstral_module as mi
import open_deepseek_module as ds      # load_api_key(), chat_with_deepseek(key, sys, user, model)
import open_grok_module as gx          # chat_with_grok(gx.client, sys, user, model)
import open_google_module as ge        # chat_with_gemini(sys, user, model), chat_with_gemma (sys, user, model)

# ---- Config: EXACTLY ONE MODEL PER PROVIDER ---------------------------------
PROMPT_DIR = "prompts_task1"
RESULTS_BASE = "results_task1_online"

OPENAI_MODEL   = "gpt-5-chat-latest"
MISTRAL_MODEL  = "mistral-large-latest"
DEEPSEEK_MODEL = "deepseek-chat"
#GROK_MODEL     = os.getenv("GROK_MODEL", "grok-4")
GROK_MODEL     = "grok-3-mini"
GEMINI_MODEL   = "gemini-2.5-pro"
GEMMA_MODEL  = "gemma-3-12b-it"

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

# ---- Helpers ----------------------------------------------------------------
def extract_grades_multi(text: str, n_expected: int) -> List[str]:
    """Extract first n_expected standalone digits 1-5 from the response."""
    body = text.split("</think>")[-1] if "</think>" in text else text
    # common formats: "1 2 3 4 5 4 3 2", "1,2,3,4,5,4,3,2", lines, etc.
    nums = re.findall(r"\b[1-5]\b", body)
    if len(nums) >= n_expected:
        return nums[:n_expected]
    # fallback: if missing, pad with ERR2 and let caller log the raw response
    return nums + ["ERR2"] * (n_expected - len(nums))
    
# ---- Helpers ----------------------------------------------------------------
# ... keep your existing extract_grades_multi / next_index / write_error_dump ...

def _call_with_retries(provider: str, cfg: dict, sys_multi: str, user_multi: str,
                       model_name: str, ctx, max_tries: int = 1):
    """
    Call the provider function with up to max_tries retries on exceptions.
    Returns (resp, attempts_used). Raises the last exception if all attempts fail.
    """
    last_exc = None
    for attempt in range(1, max_tries + 1):
        try:
            if provider in ("mistral", "deepseek"):
                return cfg["call"](sys_multi, user_multi, model_name, ctx), attempt
            else:
                return cfg["call"](sys_multi, user_multi, model_name), attempt
        except Exception as e:
            last_exc = e
            if attempt >= max_tries:
                raise
            # simple linear backoff with jitter
            time.sleep(0.6 * attempt + random.uniform(0.0, 0.4))
    # Should never get here
    raise last_exc

def next_index(dir_path: str, prefix: str) -> int:
    existing = [f for f in os.listdir(dir_path)
                if f.startswith(prefix) and f.endswith(".csv")]
    idxs = []
    for f in existing:
        m = re.search(r"_(\d+)\.csv$", f)
        if m:
            idxs.append(int(m.group(1)))
    return (max(idxs) + 1) if idxs else 1

def write_error_dump(err_path: str, sys_msg: str, uq: str, resp: str, note: str) -> None:
    print ("prompt retried")
    with open(err_path, "a", encoding="utf-8") as outf:
        outf.write("---------\n")
        outf.write("SYSTEM:\n" + sys_msg + "\n\n")
        outf.write("USER (combined):\n" + uq + "\n\n")
        outf.write("-- RAW RESPONSE --\n" + (resp or "") + "\n")
        outf.write("-- NOTE --\n" + note + "\n")
        outf.write("---------\n")

def build_combined_prompts(sys_msg: str, questions: List[str]) -> tuple[str, str]:
    """
    Keep the original system message but append a strict output-format instruction.
    No policy fallback line here; we only retry if parsing fails.
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

# ---- Load prompts once -------------------------------------------------------
prompt_files = [f for f in os.listdir(PROMPT_DIR) if f.endswith(".json")]

# ---- Main loop ---------------------------------------------------------------
for provider, cfg in PROVIDERS.items():
    # Provider-level init (client or key), optional
    ctx = None
    if "init" in cfg and callable(cfg["init"]):
        try:
            ctx = cfg["init"]()
        except Exception as e:
            print(f"\n!! Skipping provider '{provider}' due to init error: {e}")
            continue

    for model_name in cfg["models"]:
        print(f"\n?? Running prompts on provider: {provider}  model: {model_name}")
        model_dir = f"{RESULTS_BASE}_{provider}_{model_name.replace(':', '_').replace('/', '_')}"
        os.makedirs(model_dir, exist_ok=True)

        for prompt_file in prompt_files:
            lang = prompt_file.split('_')[-1].split('.')[0]  # EN, DE, SR
            prompt_path = os.path.join(PROMPT_DIR, prompt_file)
            with open(prompt_path, "r", encoding="utf-8") as pf:
                groups = json.load(pf)

            # Headers: keep per-trait columns (Target Q1..Qn) as before
            headers = []
            for grp in groups:
                target = grp["Target"]
                for i in range(len(grp["User"])):
                    headers.append(f"{target} Q{i+1}")

            # Paths
            prefix = f"results_{lang}_task1_"
            file_index = next_index(model_dir, prefix)
            out_path = os.path.join(model_dir, f"{prefix}{file_index:02d}.csv")
            err_log = os.path.join(model_dir, f"{prefix}{file_index:02d}_ERRORS.txt")

            # Collect answers
            answers: List[str] = []
            print(f"\n?? {lang} prompts on {provider}/{model_name}")

            for grp in groups:
                sys_msg = grp["System"]
                questions = grp["User"]
                sys_multi, user_multi = build_combined_prompts(sys_msg, questions)

                header_preview = f"{grp['Target']} Q1..Q{len(questions)}"
                print(f"?? [{provider}/{model_name}] {lang} {header_preview}...", end=" ")

                try:
                    max_tries = 5 if provider == "openai" else 1  # retry ChatGPT up to 5 times
                    resp, _attempts_used = _call_with_retries(provider, cfg, sys_multi, user_multi, model_name, ctx, max_tries)
                except Exception as e:
                    print(f"? error: {e}")
                    answers.extend(["ERR1"] * len(questions))
                    write_error_dump(
                        err_log, sys_multi, user_multi,
                        f"(Exception after retries) {e}",
                        f"ERR1 for all in group; provider={provider}, model={model_name}, retries={max_tries}"
                    )
                    time.sleep(0.3)
                    continue

                nums = extract_grades_multi(resp, len(questions))

                # OPTIONAL parse-retry: only for OpenAI and parser see ERR2
                if provider == "openai" and any(x == "ERR2" for x in nums):
                    parse_retries = 4  # retries +4 = max 5 
                    for k in range(parse_retries):
                        try:
                            # one retry
                            resp, _ = _call_with_retries(provider, cfg, sys_multi, user_multi, model_name, ctx, 1)
                        except Exception as e:
                            write_error_dump(
                                err_log, sys_multi, user_multi,
                                f"(Parse-retry Exception) {e}",
                                f"parse_retry={k+1}"
                            )
                            continue
                        nums = extract_grades_multi(resp, len(questions))
                        if not any(x == "ERR2" for x in nums):
                            break

                    print(" ".join(nums))
                    if any(x == "ERR2" for x in nums):
                        # write error log
                        write_error_dump(err_log, sys_multi, user_multi, resp, "Missing numbers after parse-retries (kept ERR2)")
                    answers.extend(nums)

                print(" ".join(nums))
                if any(x == "ERR2" for x in nums):
                    write_error_dump(err_log, sys_multi, user_multi, resp, "Missing numbers after parse-retries (kept ERR2)")
                answers.extend(nums)

                time.sleep(random.uniform(0.2, 0.5))

            # Save CSV
            if len(answers) != len(headers):
                missing = len(headers) - len(answers)
                if missing > 0:
                    answers.extend(["ERR3"] * missing)
            with open(out_path, "w", newline="", encoding="utf-8") as outf:
                wr = csv.writer(outf)
                wr.writerow(headers)
                wr.writerow(answers)
            print(f"? Saved: {out_path}")
