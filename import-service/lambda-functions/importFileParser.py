import os
import boto3
import csv
import json
from io import StringIO

def handler(event, context):
    s3_bucket = os.getenv('IMPORT_BUCKET_NAME', "rs-school-import-service")
    s3_client = boto3.client('s3')

    try:
        for record in event['Records']:
            key = record['s3']['object']['key']
            s3_object = s3_client.get_object(
                Bucket=s3_bucket,
                Key=key
            )
            s3_data = s3_object['Body'].read().decode('utf-8')

            csv_data = StringIO(s3_data)
            csv_reader = csv.DictReader(csv_data)
        
            for row in csv_reader:
                print(json.dumps(row))

            s3_client.copy_object(
                CopySource={'Bucket': s3_bucket, 'Key': key},
                Bucket=s3_bucket,
                Key=f'parsed/{key.split("/")[-1]}'
            )
            s3_client.delete_object(
                Bucket=s3_bucket,
                Key=key
            )

    except Exception as e:
        print(f"Error reading CSV from S3: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error reading CSV from S3: {e}")
        }
    return {
        'statusCode': 200,
        'body': json.dumps('CSV data processed successfully')
    }

if __name__ == '__main__':
    handler(None, None)