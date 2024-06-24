import os
import boto3
import uuid
import json
from common import return_error

def handler(event, lambda_context):
    try:
        product = json.loads(event['body'])
        id = uuid.uuid4()
        products_table_name = os.getenv('PRODUCTS_TABLE_NAME', "products")
        stocks_table_name = os.getenv('STOCKS_TABLE_NAME', "stocks")
        
        if not product.get('title') or not product.get('description') or not product.get('price'):
            return return_error(400, { "message": "Bad request" })

        dynamodb = boto3.client('dynamodb')
        response = dynamodb.transact_write_items(
            TransactItems=[
                {
                    'Put': {
                        'TableName': products_table_name,
                        'Item': {
                            'id': {'S': str(id)},
                            'title': {'S': product['title']},
                            'description': {'S': product['description']},
                            'price': {'N': str(product['price'])},
                        },
                        'ConditionExpression': 'attribute_not_exists(id)',
                        'ReturnValuesOnConditionCheckFailure': 'ALL_OLD'
                    }
                },
                {
                    'Put': {
                        'TableName': stocks_table_name,
                        'Item': {
                            'product_id': {'S': str(id)},
                            'count': {'N': str(product['count'] if product.get('count') else 0)},
                        },
                        'ConditionExpression': 'attribute_not_exists(product_id)',
                        'ReturnValuesOnConditionCheckFailure': 'ALL_OLD'
                    }
                }
            ]
        )
        return return_error(200, { "message": "Product was created", "id": str(id) })

    except Exception as e:
        print(e)
        return return_error(500, { "message": f"Internal server error: {str(e)}" })
    
if __name__ == "__main__":
    handler(None, None)