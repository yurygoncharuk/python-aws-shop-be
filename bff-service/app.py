from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from flask_caching import Cache

load_dotenv()
EXCLUDED_HEADERS = os.getenv('EXCLUDED_HEADERS', 'host,sec-ch-ua,sec-ch-ua-mobile,sec-ch-ua-platform,upgrade-insecure-requests,sec-fetch-site,sec-fetch-mode,sec-fetch-user,sec-fetch-dest').split(',')

app = Flask(__name__)

cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 120})

def get_service_url(service_name):
    return os.getenv(service_name.upper() + "_URL")

@cache.cached(timeout=120, key_prefix='products')
def get_products(service_name, path):
    product_url = get_service_url(service_name)
    if not product_url:
        return {"error": "Cannot process request"}, 502
    
    response = requests.get(f"{product_url}/{path}")
    return response.json(), response.status_code

@app.before_request
def before_request_func():
    if request.path == '/favicon.ico':
        return '', 204

@app.route('/<service_name>/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<service_name>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_request(service_name, path):
    print(f"Received request for service: {service_name}, path: {path}")
    recipient_url = get_service_url(service_name)
    print(f"Recipient URL: {recipient_url}")

    if not recipient_url:
        return jsonify({"error": "Cannot process request"}), 502

    method = request.method
    print(f"Method: {method}")
    #headers = dict(request.headers)
    headers = {key: value for key, value in request.headers.items() if not any(key.lower().startswith(eh) for eh in EXCLUDED_HEADERS)}
    print(f"Headers: {headers}")

    if service_name == "product" and method == "GET" and "products" in path:
        return jsonify(get_products(service_name, path))

    full_url = f"{recipient_url}/{path}"
    print(f"Full URL: {full_url}")

    try:
        if method == 'GET':
            response = requests.get(full_url, params=request.args, headers=headers)
        elif method == 'POST':
            response = requests.post(full_url, json=request.json, headers=headers)
        elif method == 'PUT':
            response = requests.put(full_url, json=request.json, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(full_url, headers=headers)
        print(f"Response status code: {response.status_code}")
        print(f"Response: {response}")
        print(f"Response text: {response.text}")
        try:
            return jsonify(response.json()), response.status_code
        except ValueError:
            return response.text, response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
