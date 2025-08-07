import json
import boto3
import os

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")


def batch_llm_inference_handler(event, context):
    # Parse S3 trigger event
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    # Read the batch prompt file from S3
    prompt_obj = s3.get_object(Bucket=bucket, Key=key)
    prompt_body = prompt_obj['Body'].read().decode('utf-8')
    prompt_list = json.loads(prompt_body)  # list of prompt blocks

    results = []

    for i, prompt_json in enumerate(prompt_list):
        # Send each prompt block to Nova Micro
        response = bedrock.invoke_model(
            modelId="amazon.nova-micro-v1:0",
            body=json.dumps(prompt_json),
            accept="application/json",
            contentType="application/json"
        )
        data = json.loads(response['body'].read())
        llm_output = data['output']['message']['content'][0]['text']

        results.append({
            "prompt_index": i,
            "prompt": prompt_json,
            "llm_output": llm_output,
            "bedrock_raw_response": data
        })

    base_filename = os.path.basename(key)
    output_key = (
        f"prompt_outputs/"
        f"{base_filename.replace('.json', '_output.json')}"
    )

    # Write the results as a list to S3
    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=json.dumps(results, indent=2).encode('utf-8')
    )

    print(
        f"Processed {len(results)} prompts from {key}, "
        f"wrote result to {output_key}"
    )

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"output_s3_uri": f"s3://{bucket}/{output_key}"}
        )
    }
