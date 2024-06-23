import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from common import return_error


def handler(event, lambda_context):
    try:
        products_table_name = os.getenv('PRODUCTS_TABLE_NAME')
        stocks_table_name = os.getenv('STOCKS_TABLE_NAME')
        
        dynamodb = boto3.resource('dynamodb')

        products_table = dynamodb.Table(products_table_name)
        stocks_table = dynamodb.Table(stocks_table_name)

        products_response = products_table.scan()
        products_items = products_response['Items']
        if not products_items:
            return return_error(404, { "message": "Products not found" })

        products = []
        for product in products_items:
            stocks_response = stocks_table.query(
                KeyConditionExpression=Key('product_id').eq(product['id'])
            )
            stocs_items = stocks_response['Items']
            if stocs_items:
                product['count'] = stocs_items[0]['count']
            else:
                product['count'] = 0
            products.append(product)

        return return_error(200, products)

    except Exception as e:
        print(e)
        return return_error(500, { "message": f"Internal server error: {str(e)}" })

if __name__ == "__main__":
    handler(None, None)