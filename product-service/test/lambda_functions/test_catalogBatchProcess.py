import json
import os
import sys
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath("lambda-functions"))
from catalogBatchProcess import handler
from common import write_to_dynamodb, return_message

os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['PRODUCTS_TABLE_NAME'] = 'products'
os.environ['STOCKS_TABLE_NAME'] = 'stocks'

@pytest.fixture
def dynamodb_mock(mocker):
    return mocker.patch('boto3.client')


@pytest.fixture
def env_setup(monkeypatch):
    monkeypatch.setenv('PRODUCTS_TABLE_NAME', 'products')
    monkeypatch.setenv('STOCKS_TABLE_NAME', 'stocks')
    monkeypatch.setenv('SNS_ARN', 'arn:aws:sns:REGION:ACCOUNT_ID:TOPIC_NAME')


def test_write_to_dynamodb_success(dynamodb_mock, env_setup):
    mock_dynamodb = MagicMock()
    dynamodb_mock.return_value = mock_dynamodb
    
    product = {
        'title': 'test_title',
        'description': 'test_description',
        'price': Decimal('19.99'),
        'count': 10
    }

    mock_dynamodb.transact_write_items.return_value = {}

    response = write_to_dynamodb(mock_dynamodb, product)

    assert response['statusCode'] == 200
    assert 'Product was created' in response['body']


def test_write_to_dynamodb_missing_fields(dynamodb_mock, env_setup):
    mock_dynamodb = MagicMock()
    dynamodb_mock.return_value = mock_dynamodb
    
    product = {
        'title': 'test_title',
        'description': 'test_description'
    }

    response = write_to_dynamodb(mock_dynamodb, product)

    assert response['statusCode'] == 400
    assert '400 Bad request' in response['body']


def test_handler_success(mocker, dynamodb_mock, env_setup):
    mock_sns = MagicMock()
    dynamodb_mock.return_value = mock_sns
    
    event = {
        'Records': [
            {
                'body': json.dumps({
                    'title': 'test_title',
                    'description': 'test_description',
                    'price': '19.99',
                    'count': 10
                })
            }
        ]
    }

    mocker.patch('common.write_to_dynamodb', return_value=return_message(200, {"message": "Product was created"}))
    
    response = handler(event, None)

    assert response['statusCode'] == 200
    assert 'Products created' in response['body']


def test_handler_failure(mocker, dynamodb_mock, env_setup):
    mock_sns = MagicMock()
    dynamodb_mock.return_value = mock_sns
    
    event = {
        'Records': [
            {
                'body': json.dumps({
                    'title': 'test_title',
                    'description': 'test_description',
                    'price': '19.99',
                    'count': 10
                })
            }
        ]
    }

    mocker.patch('common.write_to_dynamodb', side_effect=Exception("DynamoDB Error"))
    
    response = handler(event, None)

    assert response['statusCode'] == 200
    assert 'Products created' in response['body']


def test_return_message():
    response = return_message(400)
    assert response['statusCode'] == 400
    assert '400 Bad request' in response['body']
