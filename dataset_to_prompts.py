import os
import json
import zipfile
import shutil
import argparse
from datasets import load_dataset

# === CONFIG DEFAULTS ===
DATASET_NAME = "RCantini/CLEAR-Bias"   # default dataset
DATASET_CONFIG = "base_prompts"        # could also be "control_set" or "jailbreak_prompts"
TEXT_FIELD = "PROMPT"                  # correct column for CLEAR-Bias
OUTPUT_DIR = "prompts_json"            # stay inside project root
ZIP_FILE = "prompts_bundle.zip"        # bundle inside project root
OUTPUTS_DIR = "outputs"                # local folder for Lambda results
DEFAULT_LIMIT = 100

def export_prompts(limit=DEFAULT_LIMIT, clean=True):
    print(f"Loading dataset {DATASET_NAME} ({DATASET_CONFIG}) ...")
    dataset = load_dataset(DATASET_NAME, DATASET_CONFIG, split="train")

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

    count = 0
    file_list = []

    for i, row in enumerate(dataset):
        if limit and count >= limit:
            break
        if TEXT_FIELD not in row:
            continue

        prompt_text = row[TEXT_FIELD]

        prompt_json = {
            "messages": [
                {"role": "user", "content": [{"text": prompt_text}]}
            ]
        }

        filename = os.path.join(OUTPUT_DIR, f"prompt_{i}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(prompt_json, f, ensure_ascii=False, indent=2)

        file_list.append(filename)
        count += 1

    print(f"Exported {count} prompts to {OUTPUT_DIR}/")
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
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Limit the number of prompts to export")
    args = parser.parse_args()

    files = export_prompts(limit=args.limit, clean=not args.noclean)
    zip_prompts(files)
