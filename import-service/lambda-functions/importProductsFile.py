import os
import boto3
import json
import logging
from botocore.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def return_message(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Content-Type": "application/json",
        },
        'body': body
    }

def generate_presigned_url(file_name, s3_bucket):
    s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))
    key = f'uploaded/{file_name}'
    params = {
        'Bucket': s3_bucket,
        'Key': key
    }
    try:
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod='put_object',
            Params=params,
            HttpMethod='PUT'
        )
        logger.info(f"Generated presigned URL: {presigned_url}")
        return presigned_url
    except Exception as e:
        logger.error(f"Error generating presigned URL: {e}")
        raise

def handler(event, context):
    if 'queryStringParameters' not in event or 'name' not in event['queryStringParameters']:
        error_message = "Missing 'name' parameter in query string"
        logger.error(error_message)
        return return_message(400, json.dumps({"error": error_message}))

    file_name = event['queryStringParameters']['name']
    s3_bucket = os.getenv('IMPORT_BUCKET_NAME', "rs-school-import-service")

    try:
        presigned_url = generate_presigned_url(file_name, s3_bucket)
        return return_message(200, presigned_url)
    except Exception as e:
        error_message = f"500 Internal server error: {str(e)}"
        return return_message(500, json.dumps({"error": error_message}))

if __name__ == '__main__':
    # Example event to test the function
    test_event = {
        'queryStringParameters': {
            'name': 'example.txt'
        }
    }
    print(handler(test_event, None))
