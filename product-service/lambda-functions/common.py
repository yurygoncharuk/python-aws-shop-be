import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    """
    Helper class to convert a DynamoDB item to JSON.
    """
    def default(self, o):
        if isinstance(o, Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            return int(o)
        return super(DecimalEncoder, self).default(o)

def return_error(status_code, message = None):
    response = {
        400: { "message": "400 Bad request" },
        404: { "message": "404 Product not found" },
        500: { "message": "500 Internal server error"}
    }
    return {
        'statusCode': status_code,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Content-Type": "application/json",
        },
        'body': json.dumps(message if message is not None else response[status_code], cls=DecimalEncoder)
    }