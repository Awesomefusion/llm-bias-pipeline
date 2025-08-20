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
  ```bash
  pip install datasets

## Usage

Generate Prompts

`python dataset_to_prompts.py`

Run Single Prompt End-to-End

### Windows (PowerShell)

```powershell

`$inputFile="prompts_json\prompt_0.json"; $outputFile="prompt_0-output.json"; Compress-Archive -Path .\inference_lambda.py -DestinationPath .\llm-bias-pipeline-lambda.zip -Force; aws lambda update-function-code --function-name llm-bias-pipeline-lambda --zip-file fileb://llm-bias-pipeline-lambda.zip --region us-east-1; aws s3 cp $inputFile s3://llm-bias-pipeline-inputs/ --region us-east-1; Write-Host "Waiting for $outputFile..."; while (-not (aws s3 ls s3://llm-bias-pipeline-outputs/$outputFile --region us-east-1)) { Start-Sleep -Seconds 2 }; aws s3 cp s3://llm-bias-pipeline-outputs/$outputFile .\outputs\ --region us-east-1
```

### macOS / Linux (bash)

```bash
  inputFile="prompts_json/prompt_0.json"; outputFile="prompt_0-output.json"; zip -j llm-bias-pipeline-lambda.zip inference_lambda.py; aws lambda update-function-code --function-name llm-bias-pipeline-lambda --zip-file fileb://llm-bias-pipeline-lambda.zip --region us-east-1; aws s3 cp $inputFile s3://llm-bias-pipeline-inputs/ --region us-east-1; echo "Waiting for $outputFile..."; while ! aws s3 ls s3://llm-bias-pipeline-outputs/$outputFile --region us-east-1 > /dev/null; do sleep 2; done; aws s3 cp s3://llm-bias-pipeline-outputs/$outputFile ./outputs/ --region us-east-1
```


### Batch Process All Prompts

### Windows (PowerShell)

```powershell
Get-ChildItem .\prompts_json\*.json | ForEach-Object { $inputFile=$_.FullName; $fileName=$_.Name; $outputFile=$fileName -replace '\.json$','-output.json'; aws s3 cp $inputFile s3://llm-bias-pipeline-inputs/ --region us-east-1; Write-Host "Waiting for $outputFile..."; while (-not (aws s3 ls s3://llm-bias-pipeline-outputs/$outputFile --region us-east-1)) { Start-Sleep -Seconds 2 }; aws s3 cp s3://llm-bias-pipeline-outputs/$outputFile .\outputs\ --region us-east-1; Write-Host "Saved $outputFile to outputs\" }
```

### macOS / Linux (bash)

```bash
  mkdir -p ./outputs; for inputFile in $(ls ./prompts_json/prompt_*.json | sort -V); do fileName=$(basename "$inputFile"); outputFile="${fileName%.json}-output.json"; aws s3 cp "$inputFile" s3://llm-bias-pipeline-inputs/ --region us-east-1; echo "Waiting for $outputFile..."; until aws s3 ls "s3://llm-bias-pipeline-outputs/$outputFile" --region us-east-1 >/dev/null 2>&1; do sleep 2; done; aws s3 cp "s3://llm-bias-pipeline-outputs/$outputFile" ./outputs/ --region us-east-1; echo "Saved $outputFile to outputs/"; done
```

### License

MIT License — feel free to use, adapt, and improve.