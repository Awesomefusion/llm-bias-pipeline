# llm-bias-pipeline

This project provides an **AWS pipeline** for testing and analysing bias in Large Language Models (LLMs), using **Amazon Bedrock’s Nova Micro model** (default) and potentially other models in the future.  
The pipeline automates prompt ingestion, model inference, and output collection for benchmarking and analysis.

---

## How it works

1. **Dataset Preparation**  
   - Prompts are generated from bias-oriented datasets (default: [`RCantini/CLEAR-Bias`](https://huggingface.co/datasets/RCantini/CLEAR-Bias)).  
   - `dataset_to_prompts.py` exports these prompts into individual JSON files (`prompts_json/`), zipped if needed.

2. **Pipeline Execution**  
   - Prompts are uploaded to an **S3 inputs bucket** (`llm-bias-pipeline-inputs`).  
   - An **AWS Lambda** (`llm-bias-pipeline-lambda`) is triggered automatically.  
   - The Lambda calls the **Nova Micro model** on Bedrock with the prompt.  
   - Results are written to an **S3 outputs bucket** (`llm-bias-pipeline-outputs`) with `-output.json` suffix.  

3. **Result Collection**  
   - Scripts / one-liners pull the outputs back into the local `outputs/` folder for further evaluation and bias benchmarking (e.g. using LABE or custom analysis).

---

## Architecture Diagram



---

## Prerequisites

- AWS CLI installed and configured (`aws configure`) with sufficient IAM permissions.  
- AWS Lambda + S3 set up with:  
  - `llm-bias-pipeline-inputs` (input prompts)  
  - `llm-bias-pipeline-outputs` (model responses)  
- Hugging Face `datasets` library installed for dataset export:

## Usage

Generate Prompts

### Windows

`python dataset_to_prompts.py --base 200 --adv 800
`
### macOS/Linux

`python3 dataset_to_prompts.py --base 200 --adv 800
`

### Batch Process All Prompts

### Windows (PowerShell)

```powershell

$inputCount=(Get-ChildItem .\prompts_json\ -Filter *.json).Count; aws s3 cp .\prompts_json\ s3://llm-bias-pipeline-inputs/ --recursive --region us-east-1; Write-Host "✅ Uploaded $inputCount prompts to S3 inputs bucket"; $elapsed=0; Write-Host "⏳ Waiting for $inputCount outputs..."; do { $outputCount=(aws s3 ls s3://llm-bias-pipeline-outputs/ --region us-east-1 | Measure-Object).Count; Write-Host "⏳ $outputCount/$inputCount outputs ready..."; Start-Sleep -Seconds_*_
```

### macOS / Linux (bash)

```bash

inputCount=$(ls ./prompts_json/*.json | wc -l); aws s3 cp ./prompts_json/ s3://llm-bias-pipeline-inputs/ --recursive --region us-east-1 && echo "✅ Uploaded $inputCount prompts to S3 inputs bucket"; elapsed=0; echo "⏳ Waiting for $inputCount outputs..."; while true; do outputCount=$(aws s3 ls s3://llm-bias-pipeline-outputs/ --region us-east-1 | wc -l); echo "⏳ $outputCount/$inputCount outputs ready..."; if [ $outputCount -ge $inputCount ]; then echo "✅ $outputCount outputs now in S3 outputs bucket"; break; fi; sleep 5; elapsed=$((elapsed+5)); if [ $elapsed -ge 900 ]; then echo "❌ Timeout: not all outputs arrived after 15 minutes"; exit 1; fi; done; aws s3 sync s3://llm-bias-pipeline-outputs/ ./outputs/ --region us-east-1; localCount=$(ls ./outputs/*-output.json 2>/dev/null | wc -l); echo "✅ Synced $localCount outputs to ./outputs/"
```

### License

MIT License — feel free to use, adapt, and improve.