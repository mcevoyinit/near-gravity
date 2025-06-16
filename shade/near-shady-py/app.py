from flask import Flask, jsonify, request
from flask_cors import CORS
import hashlib
import requests
from typing import List, Dict, Any
import os
import dotenv

dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)

PORT = 3000
# API_PATH: "shade-agent-api" | "localhost"
API_PATH = os.getenv('API_PATH', 'shade-agent-api')  # Default to shade-agent-api if not set
API_PORT = os.getenv('API_PORT', '3140')  # Default to 3140 if not set

@app.route('/api/address', methods=['GET'])
def get_agent_account() -> Dict[str, Any]:
    """
    Gets the worker ephemeral account from the shade-agent-js api docker app.

    Returns:
        Dict[str, Any]: The agent account information

    Raises:
        requests.RequestException: If the request to the agent API fails
    """
    try:
        url = f'http://{API_PATH}:{API_PORT}/api/address'
        print(f'Requesting agent account from: {url}')
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        return response.json()
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-sign', methods=['GET'])
def sign_with_agent() -> Dict[str, Any]:
    """
    Gets a signature with the worker account using hardcoded test values.
    This matches the behavior of the JavaScript test endpoint.

    Returns:
        Dict[str, Any]: The signature response

    Raises:
        requests.RequestException: If the request to the agent API fails
    """
    try:
        path = 'foo'
        # Create SHA-256 hash of 'testing' and convert to bytes
        payload = list(hashlib.sha256(b'testing').digest())

        url = f'http://{API_PATH}:{API_PORT}/api/sign'
        response = requests.post(
            url,
            json={
                'path': path,
                'payload': payload
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f'Server listening on port: {PORT}')
    app.run(host='0.0.0.0', port=PORT)