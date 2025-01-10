import os
import logging
import json
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Define paths
TOOLSTACK_PATH = os.path.join(os.getcwd(), "Config", "toolstack.json")
SCRIPT_EXECUTOR_PATH = os.path.join(os.getcwd(), "script_executor.py")  # Path to script executor

def load_toolstack():
    """Load the toolstack.json file."""
    try:
        with open(TOOLSTACK_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Toolstack file not found at {TOOLSTACK_PATH}")
        return {"error": "Toolstack file not found"}
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse toolstack.json: {str(e)}")
        return {"error": "Invalid JSON in toolstack.json"}
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {"error": "Failed to load toolstack.json"}

@app.route('/get-toolstack', methods=['GET'])
def get_toolstack():
    """Retrieve the toolstack.json configuration."""
    try:
        toolstack = load_toolstack()
        if "error" in toolstack:
            return jsonify(toolstack), 500
        return jsonify(toolstack), 200
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/execute-task', methods=['POST'])
def execute_task():
    """Forward tasks to the script executor."""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"status": "error", "message": "Invalid or missing payload"}), 400

        # Forward the payload to the script executor
        result = subprocess.run(
            ["python", SCRIPT_EXECUTOR_PATH, json.dumps(payload)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logging.error(f"Script executor error: {result.stderr}")
            return jsonify({"status": "error", "message": result.stderr}), 500

        return jsonify(json.loads(result.stdout))
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/execute-curl', methods=['POST'])
def execute_curl():
    """Execute curl commands."""
    try:
        payload = request.get_json()
        url = payload.get("url")
        method = payload.get("method", "GET").upper()
        headers = payload.get("headers", {})
        data = payload.get("data", "")

        if not url:
            return jsonify({"status": "error", "message": "URL is required"}), 400

        curl_command = ["curl", "-X", method, url]
        for key, value in headers.items():
            curl_command += ["-H", f"{key}: {value}"]
        if data:
            curl_command += ["-d", data]

        result = subprocess.run(curl_command, capture_output=True, text=True)
        return jsonify({"status": "success", "output": result.stdout}), 200
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)