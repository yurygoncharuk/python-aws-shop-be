import os
import boto3

def handler(event, context):
    file_name = 'test.csv' #event['queryStringParameters']
    print(event)
    s3_bucket = 'rs-school-import-service' #os.environ['IMPORT_BUCKET_NAME']
    key = f'uploaded/{file_name}'
    params = {
        'Bucket': s3_bucket,
        'Key': key
    }

    region = 'eu-west-1'
    s3 = boto3.client('s3', region_name=region)
    presigned_url = s3.generate_presigned_url(
        ClientMethod = 'put_object',
        Params = params,
        ExpiresIn = 3600,
        HttpMethod = 'PUT'
    )
    print(presigned_url)
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