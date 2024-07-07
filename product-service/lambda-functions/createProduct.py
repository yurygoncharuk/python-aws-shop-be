import boto3
import json
from common import write_to_dynamodb 

def handler(event, lambda_context):
    print(json.dumps(event))
    product = json.loads(event['body'])
    dynamodb = boto3.client('dynamodb')
    response = write_to_dynamodb(dynamodb, product)
    return response
    
if __name__ == "__main__":
    handler(None, None)