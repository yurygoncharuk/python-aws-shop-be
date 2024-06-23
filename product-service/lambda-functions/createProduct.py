import os
import boto3
import uuid
from common import return_error

def handler(event, lambda_context):
    try:
        product = event['body']
        id = uuid.uuid4()
        products_table_name = os.getenv('PRODUCTS_TABLE_NAME')
        stocks_table_name = os.getenv('STOCKS_TABLE_NAME')
        
        if not product['title'] or not product['description'] or not product['price']:
            return return_error(400, { "message": "Bad request" })

        dynamodb = boto3.resource('dynamodb')
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
                        }
                    }
                },
                {
                    'Put': {
                        'TableName': stocks_table_name,
                        'Item': {
                            'product_id': {'S': str(id)},
                            'count': {'N': str(product['count'])},
                        }
                    }
                }
            ]
        )

    except Exception as e:
        print(e)
        return return_error(500, { "message": f"Internal server error: {str(e)}" })