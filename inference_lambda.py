import boto3
import json
import os

s3_client = boto3.client('s3')
bedrock_client = boto3.client('bedrock-runtime')

MODEL_ID = os.getenv('MODEL_ID', 'amazon.nova-micro-v1:0')
OUTPUT_BUCKET = os.getenv('OUTPUT_BUCKET', 'llm-bias-pipeline-outputs')

def lambda_handler(event, context):
    try:
        # Detect if this is an S3 event or direct invocation
        if "Records" in event:
            # S3 event
            for record in event['Records']:
                bucket = record['s3']['bucket']['name']
                key = record['s3']['object']['key']
                print(f"Processing file: s3://{bucket}/{key}")

                # Get the file from S3
                response = s3_client.get_object(Bucket=bucket, Key=key)
                file_content = response['Body'].read().decode('utf-8')
                prompt_json = json.loads(file_content)

                body = _format_for_bedrock(prompt_json)

                # Call Bedrock
                model_output = _call_bedrock(body)

                # Save to outputs bucket
                output_key = key.replace('.json', '-output.json')
                s3_client.put_object(
                    Bucket=OUTPUT_BUCKET,
                    Key=output_key,
                    Body=model_output
                )

        else:
            # Direct invocation
            print("Direct invocation detected")
            prompt_json = event
            body = _format_for_bedrock(prompt_json)
            model_output = _call_bedrock(body)
            return json.loads(model_output)  # Return output directly in test result

    except Exception as e:
        print(f"Error processing prompt: {e}")
        raise e

def _format_for_bedrock(prompt_json):
    """Ensure the input is in Bedrock's expected format depending on model family"""
    if MODEL_ID.startswith("meta.llama3"):
        # Llama 3 expects a single "prompt" string
        if "messages" in prompt_json:
            prompt_text = " ".join(
                part.get("text", "")
                for msg in prompt_json["messages"]
                for part in msg.get("content", [])
            )
        else:
            prompt_text = prompt_json.get("prompt", str(prompt_json))
        return json.dumps({"prompt": prompt_text})
    else:
        # Nova and similar use "messages"
        if "messages" in prompt_json:
            return json.dumps(prompt_json)
        else:
            return json.dumps({
                "messages": [
                    {"role": "user", "content": [{"text": prompt_json.get("prompt", str(prompt_json))}]}
                ]
            })

def _call_bedrock(body):
    """Invoke the Bedrock model and return the result"""
    response = bedrock_client.invoke_model(
        modelId=MODEL_ID,
        contentType='application/json',
        accept='application/json',
        body=body
    )
    return response['body'].read().decode('utf-8')
