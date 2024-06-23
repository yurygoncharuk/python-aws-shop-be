import os
import boto3
from boto3.dynamodb.conditions import Key
from common import return_error

def handler(event, lambda_context):
    try:
        product_id = event['pathParameters']['product_id']

        products_table_name = os.getenv('PRODUCTS_TABLE_NAME')
        stocks_table_name = os.getenv('STOCKS_TABLE_NAME')
        
        dynamodb = boto3.resource('dynamodb')

        products_table = dynamodb.Table(products_table_name)
        products_response = products_table.query(
            KeyConditionExpression=Key('id').eq(product_id)
        )

        product = products_response['Items']
        if product:
            stocks_table = dynamodb.Table(stocks_table_name)
            stocks_response = stocks_table.query(
                KeyConditionExpression=Key('product_id').eq(product_id)
            )
            stocs_items = stocks_response['Items']
            if stocs_items:
                product[0]['count'] = stocs_items[0]['count']
            else:
                product[0]['count'] = 0
            return return_error(200, product[0])
        else:
            return return_error(404, { "message": "Product not found" })
        
    except Exception as e:
        print(e)
        return return_error(500, { "message": f"Internal server error: {str(e)}" })

if __name__ == "__main__":
    handler(None, None)