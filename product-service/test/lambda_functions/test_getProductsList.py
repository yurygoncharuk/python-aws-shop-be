import pytest
import moto
import boto3
import os
import sys
import json

sys.path.append(os.path.abspath("lambda-functions"))
import getProductsList

os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'

@pytest.fixture
def dynamodb_mock():
    with moto.mock_aws():
        yield boto3.resource('dynamodb')

def test_empty_products_table(dynamodb_mock):
    dynamodb = dynamodb_mock
    products_table = dynamodb.create_table(
        TableName='products',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )
    stocks_table = dynamodb.create_table(
        TableName='stocks',
        KeySchema=[{'AttributeName': 'product_id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'product_id', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )

    response = getProductsList.handler(None, None)
    assert response['statusCode'] == 404

def test_non_empty_products_table_with_stock_items(dynamodb_mock):
    dynamodb = dynamodb_mock
    products_table = dynamodb.create_table(
        TableName='products',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )
    stocks_table = dynamodb.create_table(
        TableName='stocks',
        KeySchema=[{'AttributeName': 'product_id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'product_id', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )

    products_table.put_item(Item={'id': '1', 'title': 'Product 1'})
    products_table.put_item(Item={'id': '2', 'title': 'Product 2'})
    stocks_table.put_item(Item={'product_id': '1', 'count': 10})
    stocks_table.put_item(Item={'product_id': '2', 'count': 20})

    # Mock the stocks_table.query method to return the appropriate stock items
    stocks_table.query = lambda KeyConditionExpression: {'Items': [{'product_id': '1', 'count': 10}]} if KeyConditionExpression.values[0] == '1' else {'Items': [{'product_id': '2', 'count': 20}]}

    response = getProductsList.handler(None, None)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert len(body) == 2
    assert body[0]['id'] == '1' and body[0]['count'] == 10
    assert body[1]['id'] == '2' and body[1]['count'] == 20
