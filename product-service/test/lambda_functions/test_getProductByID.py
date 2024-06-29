import pytest
import moto
import boto3
import os
import sys
import json

sys.path.append(os.path.abspath("lambda-functions"))
import getProductByID

os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['PRODUCTS_TABLE_NAME'] = 'products'
os.environ['STOCKS_TABLE_NAME'] = 'stocks'

@pytest.fixture
def dynamodb_mock():
    with moto.mock_aws():
        yield boto3.resource('dynamodb')

@pytest.fixture
def valid_product_id():
    return '1'

@pytest.fixture
def invalid_product_id():
    return '2'

def test_valid_product_id(dynamodb_mock, valid_product_id):
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

    products_table.put_item(Item={'id': valid_product_id, 'title': 'Test Product'})
    stocks_table.put_item(Item={'product_id': valid_product_id, 'count': 10})

    event = {'pathParameters': {'product_id': valid_product_id}}
    response = getProductByID.handler(event, None)

    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['id'] == valid_product_id
    assert body['count'] == 10

def test_non_existent_product_id(dynamodb_mock, invalid_product_id):
    event = {'pathParameters': {'product_id': invalid_product_id}}
    response = getProductByID.handler(event, None)
    assert response['statusCode'] == 500