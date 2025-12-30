import json
import boto3
import logging
import os

# -------------------------------
# Logging Configuration
# -------------------------------
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# -------------------------------
# Bedrock Client Initialization
# -------------------------------
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

MODEL_ID = "amazon.titan-text-express-v1"


def lambda_handler(event, context):
    """
    Entry point for API Gateway -> Lambda -> Bedrock
    """
    request_id = context.aws_request_id
    logger.info(f"[{request_id}] Lambda invocation started")

    try:
        # Log incoming event metadata (not full payload)
        logger.debug(f"[{request_id}] Incoming event keys: {list(event.keys())}")

        # Parse request body
        body = json.loads(event.get("body", "{}"))
        input_text = body.get("text")

        if not input_text:
            logger.warning(f"[{request_id}] Missing 'text' field in request body")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'text' field in request body"})
            }

        logger.info(f"[{request_id}] Text received (length={len(input_text)})")

        # Construct Bedrock payload
        payload = {
            "inputText": input_text,
            "textGenerationConfig": {
                "temperature": 0.2,
                "maxTokenCount": 300,
                "topP": 0.9
            }
        }

        logger.info(f"[{request_id}] Invoking Bedrock model: {MODEL_ID}")

        # Invoke Bedrock
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json"
        )

        logger.info(f"[{request_id}] Bedrock invocation successful")

        # Parse response
        result = json.loads(response["body"].read())
        output_text = result["results"][0]["outputText"]

        logger.info(f"[{request_id}] Response generated (length={len(output_text)})")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"response": output_text})
        }

    except Exception as e:
        logger.exception(f"[{request_id}] Error during Lambda execution")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
