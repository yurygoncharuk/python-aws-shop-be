import json
import os
import boto3
from common import write_to_dynamodb, return_message

def handler(event, lambda_context):

    products_list = []
    message = "New products created successfully"

    print(json.dumps(event))
    try:
        for record in event['Records']:
            product = json.loads(record['body'])
            print(json.dumps(product))
            dynamodb = boto3.client('dynamodb')
            response = write_to_dynamodb(dynamodb, product)
            products_list.append(product)
    except Exception as e:
        print(e)
        message = "Failed to create some products"
    try:
        sns_topic = os.getenv('SNS_ARN')
        sns = boto3.client('sns')
        sns_message = {
            "message": message,
            "products": products_list
        }
        print(json.dumps(sns_message))
        response = sns.publish(
            TopicArn=sns_topic,
            Message=json.dumps(sns_message, indent=4),
            Subject='New products created',
            MessageAttributes={
                'count': {
                    'DataType': 'Number',
                    'StringValue': str(products_list[0]['count']),
                },
                'price': {
                    'DataType': 'Number',
                    'StringValue': str(products_list[0]['price']),
                },
            },
        )
        print(f"Message sent to SNS: {response}")
        return return_message(200, { "message": "Products created" })
    except Exception as e:
        print(e)
        return return_message(500, { "message": f"500 Failed to publish message to SNS: {str(e)}" })

if __name__ == "__main__":
    handler(None, None)