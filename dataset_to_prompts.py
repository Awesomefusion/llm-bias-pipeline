import os
import json
import zipfile
import shutil
import argparse
from datasets import load_dataset
from concurrent.futures import ThreadPoolExecutor, as_completed

# === CONFIG DEFAULTS ===
DATASET_NAME = "RCantini/CLEAR-Bias"
BASE_CONFIG = "base_prompts"
ADV_CONFIG = "jailbreak_prompts"
TEXT_FIELD = "PROMPT"
OUTPUT_DIR = "prompts_json"
ZIP_FILE = "prompts_bundle.zip"
OUTPUTS_DIR = "outputs"

def write_prompt(file_path, text, idx, total):
    """Helper to write one prompt JSON file (skips if exists)"""
    if os.path.exists(file_path):
        print(f"[{idx+1}/{total}] Skipping {file_path} (already exists)", end="\r")
        return file_path

    prompt_json = {
        "messages": [
            {"role": "user", "content": [{"text": text}]}
        ]
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(prompt_json, f, ensure_ascii=False, indent=2)

    print(f"[{idx+1}/{total}] Wrote {file_path}", end="\r")
    return file_path

def export_prompts(limit_base=200, limit_adv=800, clean=True, workers=8):
    file_list = []

    # Clean old files if enabled
    if clean:
        if os.path.exists(OUTPUT_DIR):
            shutil.rmtree(OUTPUT_DIR)
        if os.path.exists(OUTPUTS_DIR):
            shutil.rmtree(OUTPUTS_DIR)
        if os.path.exists(ZIP_FILE):
            os.remove(ZIP_FILE)

    # Ensure fresh directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # === Load datasets ===
    print(f"Loading {limit_base} prompts from {DATASET_NAME} ({BASE_CONFIG}) ...")
    base_ds = load_dataset(DATASET_NAME, BASE_CONFIG, split="train")
    base_ds = base_ds.select(range(min(limit_base, len(base_ds))))

    print(f"Loading {limit_adv} prompts from {DATASET_NAME} ({ADV_CONFIG}) ...")
    adv_ds = load_dataset(DATASET_NAME, ADV_CONFIG, split="train")
    adv_ds = adv_ds.select(range(min(limit_adv, len(adv_ds))))

    combined = list(base_ds) + list(adv_ds)
    total = len(combined)

    # === Write prompts in parallel ===
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for idx, row in enumerate(combined):
            if TEXT_FIELD not in row:
                continue
            filename = os.path.join(OUTPUT_DIR, f"prompt_{idx}.json")
            futures.append(executor.submit(write_prompt, filename, row[TEXT_FIELD], idx, total))

        for f in as_completed(futures):
            file_list.append(f.result())

    print(f"\nExported {len(file_list)} prompts to {OUTPUT_DIR}/")
    return file_list

def zip_prompts(file_list):
    with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in file_list:
            arcname = os.path.basename(file)
            zipf.write(file, arcname=arcname)
    print(f"Zipped {len(file_list)} files into {ZIP_FILE}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export prompts from CLEAR-Bias dataset.")
    parser.add_argument("--noclean", action="store_true", help="Do not clean old prompts/outputs/bundle before run")
    parser.add_argument("--base", type=int, default=200, help="Number of base prompts to export")
    parser.add_argument("--adv", type=int, default=800, help="Number of adversarial prompts to export")
    parser.add_argument("--workers", type=int, default=8, help="Parallel workers for file writing")
    args = parser.parse_args()

    files = export_prompts(
        limit_base=args.base,
        limit_adv=args.adv,
        clean=not args.noclean,
        workers=args.workers
    )
    zip_prompts(files)
