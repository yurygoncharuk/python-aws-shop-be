import boto3
import json
from common import write_to_dynamodb, return_message 

def handler(event, lambda_context):
    try:
        print(json.dumps(event))
        product = json.loads(event['body'])
        dynamodb = boto3.client('dynamodb')
        response = write_to_dynamodb(dynamodb, product)
        return response
    
    except KeyError as ke:
        # Handle missing key errors
        print(f"Error: {ke}")
        return return_message(400, {"message": f"Missing required key: {ke}"})

    except Exception as e:
        # Handle generic exceptions
        print(f"Error: {e}")
        return return_message(500, {"message": f"Failed to create new product: {e}"})
    
if __name__ == "__main__":
    handler(None, None)