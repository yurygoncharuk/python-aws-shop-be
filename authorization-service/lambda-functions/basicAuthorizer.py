import os
import base64
import json
import re

def generatePolicy(principal_id, effect, resource):
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource,
            }]
        }
    }
    print(json.dumps(policy))
    return policy

def handler(event, context):
    print(json.dumps(event))

    auth_header = event.get('authorizationToken')

    if not auth_header:
        return generatePolicy("Undefined", 'Deny', event['methodArn'])
    
    auth_type, encoded_credentials = auth_header.split(' ')
    
    if auth_type.lower() != 'basic':
        return generatePolicy("Undefined", 'Deny', event['methodArn'])
    
    try:
        encoded_credentials = encoded_credentials.strip()
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = re.split(r'[=:]', decoded_credentials)
    except (ValueError, UnicodeDecodeError):
        return generatePolicy("Undefined", 'Deny', event['methodArn'])

    stored_password = os.getenv(username)
    if stored_password and stored_password == password:
        return generatePolicy(username, 'Allow', event['methodArn'])
    else:
        return generatePolicy(username, 'Deny', event['methodArn'])

if __name__ == '__main__':
    env = {
        "type": "TOKEN",
        "methodArn": "XXXXXXXXXXXXXXXXXXXX",
        "authorizationToken": "Basic eXVyeWdvbmNoYXJ1az1URVNUX1BBU1NXT1J"
    }
    handler(env, None)