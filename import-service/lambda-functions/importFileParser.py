import os
import boto3
import csv
import json
from io import StringIO

def handler(event, context):
    s3_bucket = os.getenv('IMPORT_BUCKET_NAME', "rs-school-import-service")
    sqs_url = os.getenv('SQS_URL', "")

    s3_client = boto3.client('s3')
    sqs_client = boto3.client('sqs')

    try:
        for record in event['Records']:
            key = record['s3']['object']['key']
            s3_object = s3_client.get_object(Bucket=s3_bucket, Key=key)
            s3_data = s3_object['Body'].read().decode('utf-8')

            csv_data = StringIO(s3_data)
            csv_reader = csv.DictReader(csv_data)
            entries = []
            for row in csv_reader:
                entry = json.dumps(row)
                entries.append({
                    "Id": row['title'],
                    "MessageBody": entry
                })

            print(json.dumps(entries))
            if entries:
                response = sqs_client.send_message_batch(
                    QueueUrl=sqs_url,
                    Entries=entries
                )
                if 'Failed' in response:
                    raise Exception(f"Failed to send messages: {response['Failed']}")
                print("Messages were sent to SQS")

            s3_client.copy_object(
                CopySource={'Bucket': s3_bucket, 'Key': key},
                Bucket=s3_bucket,
                Key=f'parsed/{key.split("/")[-1]}'
            )
            s3_client.delete_object(Bucket=s3_bucket, Key=key)
            print(f"Processed and moved file {key}")

    except Exception as e:
        error_message = f"Error processing file {key if 'key' in locals() else 'unknown'}: {e}"
        print(error_message)
        return {
            'statusCode': 500,
            'body': json.dumps(error_message)
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps('CSV data processed successfully')
    }

if __name__ == '__main__':
    handler(None, None)