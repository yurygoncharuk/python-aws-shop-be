import json
import os
import boto3
from common import write_to_dynamodb, return_message

def handler(event, lambda_context):
    try:
        # Initialize clients
        dynamodb = boto3.client('dynamodb')
        sns = boto3.client('sns')
        sns_topic = os.getenv('SNS_ARN')
        
        products_list = []

        # Check if 'Records' key exists in event
        records = event.get('Records', [])
        if not records:
            raise ValueError("No records found in the event")

        # Process each record
        for record in records:
            product = json.loads(record['body'])
            write_to_dynamodb(dynamodb, product)
            products_list.append(product)

        # Prepare batch publish
        entries = [{
            'Id': str(i),
            'Message': json.dumps({
                "message": "New products created successfully",
                "products": product
            }, indent=4),
            'MessageAttributes': {
                'count': {
                    'DataType': 'Number',
                    'StringValue': str(product.get('count', 0)),
                },
                'price': {
                    'DataType': 'Number',
                    'StringValue': str(product.get('price', 0)),
                },
            }
        } for i, product in enumerate(products_list)]

        print(json.dumps(entries))
        response = sns.publish_batch(
            TopicArn=sns_topic,
            PublishBatchRequestEntries=entries
        )

        print(f"Messages sent to SNS: {response}")

        # Return success message
        return return_message(200, {"message": "Products created"})

    except ValueError as ve:
        # Handle specific error for missing records
        print(f"Error: {ve}")
        return return_message(400, {"message": f"Invalid event format: {ve}"})

    except KeyError as ke:
        # Handle missing key errors
        print(f"Error: {ke}")
        return return_message(400, {"message": f"Missing required key: {ke}"})

    except Exception as e:
        # Handle generic exceptions
        print(f"Error: {e}")
        return return_message(500, {"message": f"Failed to process: {e}"})

if __name__ == "__main__":
    # For testing locally
    handler(None, None)