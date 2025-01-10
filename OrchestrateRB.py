from flask import Flask, request, jsonify
import subprocess
import os
import json

app = Flask(__name__)

TOOLSTACK_PATH = os.path.join(os.getcwd(), "Config", "toolstack.json")

def load_toolstack():
    """Load the toolstack.json file."""
    try:
        with open(TOOLSTACK_PATH, "r") as file:
            return json.load(file)
    except Exception as e:
        return {"error": f"Failed to load toolstack.json: {str(e)}"}

@app.route('/get-toolstack', methods=['GET'])
def get_toolstack():
    """Return the contents of toolstack.json."""
    return jsonify(load_toolstack())

@app.route('/execute-task', methods=['POST'])
def execute_task():
    """Delegate task execution to script_executor.py."""
    data = request.json
    tool = data.get("tool")
    task = data.get("task")
    params = data.get("params", {})

    toolstack = load_toolstack()
    if tool not in toolstack:
        return jsonify({"error": f"Tool '{tool}' not found in toolstack."}), 400

    tool_config = toolstack[tool]
    script_path = os.path.join("Scripts", tool_config["path"])
    payload = {"task": task, "params": params}

    try:
        result = subprocess.run(
            ["python", "Scripts/script_executor.py", script_path, json.dumps(payload)],
            capture_output=True,
            text=True,
            check=True
        )
        return jsonify(json.loads(result.stdout))
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Execution failed: {e.stderr}"}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON response from script"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)