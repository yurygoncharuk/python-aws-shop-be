import os
import sys
import boto3
import json
import pytest
from unittest import mock
sys.path.append(os.path.abspath("lambda-functions"))
import importFileParser

os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['IMPORT_BUCKET_NAME'] = 'rs-school-import-service'
os.environ['SQS_URL'] = 'https://sqs.us-east-1.amazonaws.com/123456789012/test-queue'  # Replace with your actual SQS URL
bucket_name = os.getenv('IMPORT_BUCKET_NAME', "rs-school-import-service")
sqs_url = os.getenv('SQS_URL', "")

@pytest.fixture
def aws_setup():
    with mock.patch('boto3.client') as mock_client:
        s3_mock = mock_client.return_value
        sqs_mock = mock_client.return_value
        
        # Mock S3 client methods
        s3_mock.create_bucket.return_value = {}
        s3_mock.delete_object.return_value = {}
        s3_mock.get_object.side_effect = lambda Bucket, Key: {'Body': mock.Mock(read=mock.Mock(return_value=b'Test content'))} if Key == 'uploaded/test.csv' else None
        s3_mock.put_object.return_value = {}
        
        # Mock SQS client methods
        queue_url = 'https://sqs.us-east-1.amazonaws.com/123456789012/test-queue'
        sqs_mock.get_queue_url.return_value = {'QueueUrl': queue_url}
        sqs_mock.receive_message.return_value = {'Messages': [{'MessageId': '1', 'Body': '{"Message": "test"}'}]}
        sqs_mock.send_message_batch.return_value = {'Successful': [{'Id': '1'}]}
        
        yield s3_mock, sqs_mock

def test_handler_success(aws_setup):
    s3_mock, sqs_mock = aws_setup
    
    # Simulate uploading a valid CSV file
    event = {
        'Records': [
            {
                's3': {
                    'object': {
                        'key': 'uploaded/test.csv'
                    }
                }
            }
        ]
    }
    
    response = importFileParser.handler(event, None)
    
    # Assert Lambda function behavior
    assert response['statusCode'] == 200
    assert response['body'] == json.dumps('CSV data processed successfully')

def test_handler_failure(aws_setup):
    s3_mock, sqs_mock = aws_setup
    
    # Simulate processing a non-existent CSV file
    event = {
        'Records': [
            {
                's3': {
                    'object': {
                        'key': 'uploaded/nonexistent.csv'
                    }
                }
            }
        ]
    }
    
    response = importFileParser.handler(event, None)
    
    # Assert Lambda function behavior
    assert response['statusCode'] == 500
    assert 'Error processing file uploaded/nonexistent.csv' in response['body']
