import os
import boto3

def handler(event, context):
    s3_bucket = 'rs-school-import-service' #os.environ['IMPORT_BUCKET_NAME']

    print(event)
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }

if __name__ == '__main__':
    handler(None, None)