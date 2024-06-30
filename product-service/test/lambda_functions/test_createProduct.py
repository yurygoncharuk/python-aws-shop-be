# import pytest
# import moto
# import boto3
# import os
# import sys
# import json

# sys.path.append(os.path.abspath("lambda-functions"))
# import getProductByID

# os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
# os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
# os.environ['AWS_SECURITY_TOKEN'] = 'testing'
# os.environ['AWS_SESSION_TOKEN'] = 'testing'
# os.environ['PRODUCTS_TABLE_NAME'] = 'products'
# os.environ['STOCKS_TABLE_NAME'] = 'stocks'

# @pytest.fixture
# def dynamodb_mock():
#     with moto.mock_aws():
#         yield boto3.client('dynamodb')

# @pytest.fixture
# def valid_product():
#     return {
#         'title': 'Test Product',
#         'description': 'This is a test product',
#         'price': 9.99,
#         'count': 10
#     }

# def test_missing_required_fields(valid_product):
#     # Remove the 'title' field
#     del valid_product['title']
#     event = {'body': json.dumps(valid_product)}
#     response = getProductByID.handler(event, None)
#     assert response['statusCode'] == 500

# def test_successful_product_creation(dynamodb_mock, valid_product):
#     dynamodb_mock.transact_write_items = {}
#     event = {'body': json.dumps(valid_product)}
#     response = getProductByID.handler(event, None)
#     assert response['statusCode'] == 500
#     body = json.loads(response['body'])
#     assert 'message' in body
#     assert 'id' in body