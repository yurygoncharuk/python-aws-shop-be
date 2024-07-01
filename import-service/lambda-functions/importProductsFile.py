import os
import boto3
from botocore.config import Config
import json

def handler(event, context):
    file_name = event['queryStringParameters']['name']
    s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))
    s3_bucket = os.getenv('IMPORT_BUCKET_NAME', "rs-school-import-service")
    key = f'uploaded/{file_name}'
    params = {
        'Bucket': s3_bucket,
        'Key': key
    }

    try:
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod = 'put_object',
            Params = params,
            HttpMethod = 'PUT'
        )
        print(presigned_url)
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json",
            },
            'body': json.dumps(f"500 Internal server error: {str(e)}")
        }
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Content-Type": "application/json",
        },
        'body': presigned_url
    }

if __name__ == '__main__':
    handler(None, None)