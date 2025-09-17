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

## Batch Process All Prompts

### Windows (PowerShell)

```
$inputFiles=Get-ChildItem .\prompts_json\ -Filter *.json|Select-Object -Expand Name;$inputCount=$inputFiles.Count;aws s3 cp .\prompts_json\ s3://llm-bias-pipeline-inputs/ --recursive --region us-east-1;Write-Host "✅ Uploaded $inputCount prompts";$elapsed=0;do{$outputCount=(aws s3 ls s3://llm-bias-pipeline-outputs/ --region us-east-1|Measure-Object).Count;Write-Host "⏳ $outputCount/$inputCount outputs... (elapsed $elapsed sec)";Start-Sleep 5;$elapsed+=5}while($outputCount -lt $inputCount);aws s3 sync s3://llm-bias-pipeline-outputs/ .\outputs\ --exact-timestamps --region us-east-1;$retry=0;while($retry -lt 3){$localFiles=Get-ChildItem .\outputs\ -Filter *-output.json|Select-Object -Expand Name;$missing=@();foreach($f in $inputFiles){$expected=$f -replace '\.json$','-output.json';if($localFiles -notcontains $expected){$missing+=$expected}};if($missing.Count -eq 0){Write-Host "🎉 All $inputCount outputs synced!";break}else{Write-Host "⚠️ Missing $($missing.Count), retrying ($retry+1/3)...";foreach($m in $missing){aws s3 cp "s3://llm-bias-pipeline-outputs/$m" .\outputs\ --region us-east-1};$retry++}};Write-Host "🔁 Done. Final count: $((Get-ChildItem .\outputs\ -Filter *-output.json).Count)/$inputCount"
```

### macOS / Linux (bash)

```
inputFiles=$(ls ./prompts_json/*.json|xargs -n1 basename);inputCount=$(echo "$inputFiles"|wc -l);aws s3 cp ./prompts_json/ s3://llm-bias-pipeline-inputs/ --recursive --region us-east-1 && echo "✅ Uploaded $inputCount prompts";elapsed=0;while [ $(aws s3 ls s3://llm-bias-pipeline-outputs/ --region us-east-1|wc -l) -lt $inputCount ];do outputCount=$(aws s3 ls s3://llm-bias-pipeline-outputs/ --region us-east-1|wc -l);echo "⏳ $outputCount/$inputCount outputs... (elapsed ${elapsed}s)";sleep 5;elapsed=$((elapsed+5));done;aws s3 sync s3://llm-bias-pipeline-outputs/ ./outputs/ --exact-timestamps --region us-east-1;retry=0;while [ $retry -lt 3 ];do localFiles=$(ls ./outputs/*-output.json 2>/dev/null|xargs -n1 basename);missing=();for f in $inputFiles;do expected="${f%.json}-output.json";if ! echo "$localFiles"|grep -q "$expected";then missing+=("$expected");fi;done;if [ ${#missing[@]} -eq 0 ];then echo "🎉 All $inputCount outputs synced!";break;else echo "⚠️ Missing ${#missing[@]} outputs, retrying $((retry+1))/3...";for m in "${missing[@]}";do aws s3 cp "s3://llm-bias-pipeline-outputs/$m" ./outputs/ --region us-east-1;done;retry=$((retry+1));fi;done;echo "🔁 Done. Final count: $(ls ./outputs/*-output.json 2>/dev/null|wc -l)/$inputCount"
```

## Run Bias Analysis

`python analyse_bias_labe.py --provider openai`

`python analyse_bias_labe.py --provider bedrock`

`python analyse_bias_labe.py --provider openai --model gpt-4o-mini --limit 0`

## Bias Visualisation

`python visualise_bias_results.py bias_eval_results_openai_gpt-4o-mini.json --output chart.png`

### License

MIT License — feel free to use, adapt, and improve.