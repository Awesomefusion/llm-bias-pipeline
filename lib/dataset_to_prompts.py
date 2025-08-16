import os
import json
import zipfile
from datasets import load_dataset

# === CONFIG ===
DATASET_NAME = "RCantini/CLEAR-Bias"   # default dataset, can be changed
TEXT_FIELD = "text"
OUTPUT_DIR = os.path.join("..", "prompts_json")
ZIP_FILE = os.path.join("..", "prompts_bundle.zip")
LIMIT = 100

def export_prompts():
    print(f"Loading dataset {DATASET_NAME} ...")
    dataset = load_dataset(DATASET_NAME, split="train")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    count = 0
    file_list = []

    for i, row in enumerate(dataset):
        if LIMIT and count >= LIMIT:
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
    files = export_prompts()
    zip_prompts(files)
