import json
import os

def handler(event, lambda_context):
    products = json.loads(os.getenv('MOCK_PRODUCTS'))
    product_id = event['pathParameters']['product_id']
    product = next((p for p in products if p['id'] == product_id), None)

    if product:
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type",
                "Content-Type": "application/json",
            },
            'body': json.dumps(product)
        }
    else:
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

