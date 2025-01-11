import os
import subprocess
import logging
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Define the path to the toolstack.json
TOOLSTACK_PATH = os.path.join(os.getcwd(), "Config", "toolstack.json")


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
        logging.error(f"Unexpected error while loading toolstack.json: {str(e)}")
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
    """Execute tasks based on the toolstack configuration."""
    try:
        # Log raw request data for debugging
        raw_data = request.data.decode('utf-8')
        logging.info(f"Raw request data: {raw_data}")

        # Parse the input payload
        data = request.get_json()
        logging.info(f"Parsed JSON payload: {data}")
        if not data:
            return jsonify({"status": "error", "message": "Invalid or missing payload"}), 400

        tool = data.get("tool")
        task = data.get("task")
        params = data.get("params", {})

        # Load toolstack
        toolstack = load_toolstack()
        if "error" in toolstack:
            return jsonify(toolstack), 500
        if tool not in toolstack:
            logging.error(f"Tool '{tool}' not found in toolstack.")
            return jsonify({"status": "error", "message": f"Tool '{tool}' not found in toolstack."}), 400

        # Route GitHub tasks
        if tool == "github":
            return handle_github_task(task, params)

        # Unsupported tool fallback
        logging.error(f"Unsupported tool '{tool}'")
        return jsonify({"status": "error", "message": f"Unsupported tool '{tool}'."}), 400

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


def handle_github_task(task, params):
    """Handle GitHub-specific tasks."""
    repo_path = "/Users/srinivas/orchestrate-rebuild/"  # Git repository path

    try:
        if task == "force_apply_changes":
            logging.info("Executing force_apply_changes task.")
            path = params.get("path")
            content = params.get("content", "Force applied content.")
            if not path:
                return jsonify({"status": "error", "message": "File path is required"}), 400

            # Write to the specified file
            full_path = os.path.join(repo_path, path)
            with open(full_path, "w") as f:
                f.write(content)
            logging.info(f"File '{path}' updated successfully.")
            return jsonify({"status": "success", "message": f"File '{path}' has been updated with provided content."})

        # Other Git operations (e.g., git_add, commit_changes, etc.)
        # ...

        else:
            logging.error(f"Unsupported GitHub task: {task}")
            return jsonify({"status": "error", "message": f"Unsupported GitHub task: {task}"}), 400

    except Exception as e:
        logging.error(f"Error during GitHub task execution: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route('/execute-script', methods=['POST'])
def execute_script():
    """Execute a script on the server."""
    try:
        script_path = request.json.get("script_path")
        result = subprocess.run(
            ["python3", script_path], capture_output=True, text=True
        )
        return jsonify({"output": result.stdout, "error": result.stderr})
    except Exception as e:
        logging.error(f"Script execution failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/self-test', methods=['GET'])
def self_test():
    """Run self-diagnostics for the server."""
    results = {}
    try:
        health_response = app.test_client().get('/health')
        results["health"] = {
            "status": health_response.status_code,
            "response": health_response.json
        }
    except Exception as e:
        results["health"] = {"error": str(e)}

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)