import json
import os
import uuid
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    """
    Helper class to convert a DynamoDB item to JSON.
    """
    def default(self, o):
        if isinstance(o, Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            return int(o)
        return super().default(o)

def return_message(status_code, message=None):
    response = {
        400: { "message": "400 Bad request" },
        404: { "message": "404 Product not found" },
        500: { "message": "500 Internal server error" }
    }
    return {
        'statusCode': status_code,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Content-Type": "application/json",
        },
        'body': json.dumps(message if message else response.get(status_code), cls=DecimalEncoder)
    }

def write_to_dynamodb(dynamodb, product):
    try:
        products_table_name = os.getenv('PRODUCTS_TABLE_NAME', "products")
        stocks_table_name = os.getenv('STOCKS_TABLE_NAME', "stocks")
        if not product.get('id'):
            product['id'] = str(uuid.uuid4())
        print(f"Product: {product}")

        if not all(key in product for key in ['title', 'description', 'price']):
            return return_message(400, { "message": "Missing required fields" })

        response = dynamodb.transact_write_items(
            TransactItems=[
                {
                    'Put': {
                        'TableName': products_table_name,
                        'Item': {
                            'id': {'S': product['id']},
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
                            'product_id': {'S': product['id']},
                            'count': {'N': str(product.get('count', 0))}
                        },
                        'ConditionExpression': 'attribute_not_exists(product_id)',
                        'ReturnValuesOnConditionCheckFailure': 'ALL_OLD'
                    }
                }
            ]
        )
        print(f"Product was added to DynamoDB: {response}")
        return return_message(200, { "message": "Product was created", "product": product })

    except KeyError as e:
        print(f"Missing required key: {e}")
        raise

    except Exception as e:
        print(f"Internal server error: {e}")
        raise