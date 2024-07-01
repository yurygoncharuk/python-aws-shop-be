import os
import sys
import boto3
import json
import pytest
import moto
sys.path.append(os.path.abspath("lambda-functions"))
import importFileParser

os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['IMPORT_BUCKET_NAME'] = 'rs-school-import-service'
bucket_name = os.getenv('IMPORT_BUCKET_NAME', "rs-school-import-service")

@pytest.fixture
def s3_setup():
    with moto.mock_aws():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket=bucket_name)
        yield

def test_handler_success(s3_setup):
    s3 = boto3.client('s3', region_name='us-east-1')
    test_csv_content = "name,age\nJohn Doe,30\nJane Smith,25"
    s3.put_object(Bucket=bucket_name, Key='uploaded/test.csv', Body=test_csv_content)

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

    assert response['statusCode'] == 200
    assert response['body'] == json.dumps('CSV data processed successfully')

    # Check if the file has been copied to the 'parsed' folder
    copied_object = s3.get_object(Bucket=bucket_name, Key='parsed/test.csv')
    assert copied_object['Body'].read().decode('utf-8') == test_csv_content

    # Check if the original file has been deleted
    with pytest.raises(s3.exceptions.NoSuchKey):
        s3.get_object(Bucket=bucket_name, Key='uploaded/test.csv')

def test_handler_failure(s3_setup):
    s3 = boto3.client('s3', region_name='us-east-1')

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

    assert response['statusCode'] == 500
    assert 'Error reading CSV from S3' in response['body']
