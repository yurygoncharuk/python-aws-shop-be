import json
import os

def handler(event, lambda_context):
    products = json.loads(os.getenv('MOCK_PRODUCTS'))
    if products is None:
        return {
            'statusCode': 404,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json",
            },
            'body': json.dumps({ "message": "Product not found" })
        }
    else:
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json",
            },
            'body': json.dumps(products)
        }
