import json
import sys
import os
import unittest

sys.path.append(os.path.abspath("lambda-functions"))
import getProductByID

class TestHandlerReturnProduct(unittest.TestCase):
    def test_lambda_handler(self):
        f = open('lambda-functions/products.json', "r")
        os.environ["MOCK_PRODUCTS"] = f.read()
        f.close()
        product_id = "1"
        event = {
            "pathParameters": {
                "product_id": product_id
            }
        }  # Mock event
        context = {}  # Mock context
        response = getProductByID.handler(event, context)
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body["id"], product_id)

class TestHandlerReturn404(unittest.TestCase):
    def test_lambda_handler(self):
        f = open('lambda-functions/products.json', "r")
        os.environ["MOCK_PRODUCTS"] = f.read()
        f.close()
        product_id = "10"
        event = {
            "pathParameters": {
                "product_id": product_id
            }
        }  # Mock event
        context = {}  # Mock context
        response = getProductByID.handler(event, context)
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertEqual(body["message"], "Product not found")

if __name__ == '__main__':
    unittest.main()