import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
bedrock_client = boto3.client('bedrock-runtime')

OUTPUT_BUCKET = os.environ['OUTPUT_BUCKET']
MODEL_ID = os.environ.get('MODEL_ID', 'amazon.nova-micro-v1:0')

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            logger.info(f"Processing file: s3://{bucket}/{key}")

            # Get prompt from S3
            obj = s3_client.get_object(Bucket=bucket, Key=key)
            prompt_data = obj['Body'].read().decode('utf-8')
            logger.info(f"Prompt content: {prompt_data}")

            # Call LLM model via Bedrock
            response = bedrock_client.invoke_model(
                modelId=MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "inputText": prompt_data,
                    "textGenerationConfig": {
                        "maxTokenCount": 512,
                        "temperature": 0.7,
                        "topP": 0.9
                    }
                })
            )

            model_output = json.loads(response['body'].read())
            logger.info(f"Model output: {model_output}")

            # Save to output S3 bucket
            output_key = key.replace("prompt_inputs", "prompt_outputs")
            s3_client.put_object(
                Bucket=OUTPUT_BUCKET,
                Key=output_key,
                Body=json.dumps(model_output, indent=2)
            )

            logger.info(f"Output saved to: s3://{OUTPUT_BUCKET}/{output_key}")

    except Exception as e:
        logger.error(f"Error processing prompt: {str(e)}", exc_info=True)
        raise e
