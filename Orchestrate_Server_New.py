import os
import json
import logging
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Path to toolstack.json
TOOLSTACK_PATH = "/Users/srinivas/Dropbox/1. Projects/Orchestrate/Orchestrate Modular/Config/toolstack.json"

def load_toolstack():
    """Load the toolstack.json configuration."""
    try:
        with open(TOOLSTACK_PATH, "r") as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Error loading toolstack.json: {e}")
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
    """Execute tasks dynamically based on toolstack.json."""
    try:
        # Load the incoming payload
        payload = request.get_json()
        logging.info(f"Payload received in /execute-task: {json.dumps(payload, indent=2)}")

        # Validate payload structure
        tool = payload.get("tool")
        task = payload.get("task")
        params = payload.get("params", {})

        if not tool or not task:
            return jsonify({"status": "error", "message": "Payload must include 'tool' and 'task'."}), 400

        # Load toolstack
        toolstack = load_toolstack()
        if tool not in toolstack:
            logging.error(f"Unsupported tool: {tool}")
            return jsonify({"status": "error", "message": f"Unsupported tool: {tool}"}), 400

        tool_config = toolstack[tool]
        if task not in tool_config.get("tasks", {}):
            logging.error(f"Unsupported task: {tool}/{task}")
            return jsonify({"status": "error", "message": f"Unsupported task: {tool}/{task}"}), 400

        # Determine the script path for the tool
        script_path = tool_config.get("path")
        if not script_path or not os.path.exists(script_path):
            logging.error(f"Invalid or missing script path for tool: {tool}")
            return jsonify({"status": "error", "message": f"Invalid or missing script path for tool: {tool}"}), 400

        # Forward the payload to the script
        result = subprocess.run(
            ["python", script_path, json.dumps(payload)],
            capture_output=True,
            text=True
        )
        logging.info(f"Script executed: {script_path} with task: {task}")

        # Check execution result
        if result.returncode != 0:
            logging.error(f"Script error: {result.stderr.strip()}")
            return jsonify({"status": "error", "message": result.stderr.strip()}), 500

        # Return the result from the script
        return jsonify(json.loads(result.stdout))

    except Exception as e:
        logging.error(f"Unexpected error in /execute-task: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/execute-curl', methods=['POST'])
def execute_curl():
    """Execute an HTTP request based on the payload."""
    try:
        payload = request.get_json()
        url = payload.get("url")
        method = payload.get("method", "GET").upper()
        headers = payload.get("headers", {})
        data = payload.get("data", "")

        if not url:
            return jsonify({"status": "error", "message": "URL is required for execute_curl."}), 400

        # Construct the curl command
        curl_command = ["curl", "-X", method, url]
        for key, value in headers.items():
            curl_command += ["-H", f"{key}: {value}"]
        if data:
            curl_command += ["-d", data]

        # Execute the curl command
        result = subprocess.run(curl_command, capture_output=True, text=True)
        return jsonify({"status": "success", "output": result.stdout.strip()}), 200

    except Exception as e:
        logging.error(f"Unexpected error in /execute-curl: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)