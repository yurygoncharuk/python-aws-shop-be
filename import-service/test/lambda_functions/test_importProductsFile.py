import os
import sys
import boto3
import pytest
from unittest.mock import patch, MagicMock
import moto
sys.path.append(os.path.abspath("lambda-functions"))
import importProductsFile

os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['IMPORT_BUCKET_NAME'] = 'rs-school-import-service'
bucket_name = os.getenv('IMPORT_BUCKET_NAME', "rs-school-import-service")
# Event to pass to the handler
event = {
    'queryStringParameters': {
        'name': 'testfile.txt'
    }
}

@pytest.fixture
def s3_setup():
    with moto.mock_aws():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket=bucket_name)
        yield

@patch('importProductsFile.boto3.client')
def test_handler_success(mock_boto_client, s3_setup):
    # Mock the S3 client
    mock_s3_client = MagicMock()
    mock_boto_client.return_value = mock_s3_client

    ## Generate a presigned URL
    presigned_url = f'https://{bucket_name}.s3.amazonaws.com/uploaded/test.csv?presigned-url'
    mock_s3_client.generate_presigned_url.return_value = presigned_url

    # Call the handler
    response = importProductsFile.handler(event, None)

    # Check the response
    assert response['statusCode'] == 200
    assert 'https://rs-school-import-service.s3.amazonaws.com/uploaded/test.csv?presigned-url' in response['body']

@patch('importProductsFile.boto3.client')
def test_handler_failure(mock_boto_client, s3_setup):
    # Mock the S3 client to raise an exception
    mock_s3_client = MagicMock()
    mock_s3_client.generate_presigned_url.side_effect = Exception("Test exception")
    mock_boto_client.return_value = mock_s3_client

    # Call the handler
    response = importProductsFile.handler(event, None)

    # Check the response
    assert response['statusCode'] == 500
    assert '500 Internal server error' in response['body']