from flask import Flask, request, jsonify
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Path to toolstack.json
TOOLSTACK_PATH = "/Users/srinivas/Dropbox/1. Projects/Orchestrate/Orchestrate Modular/Config/toolstack.json"

# Load toolstack.json at startup
try:
    with open(TOOLSTACK_PATH, "r") as file:
        toolstack = json.load(file)
except FileNotFoundError:
    raise FileNotFoundError(f"Critical Error: toolstack.json not found at {TOOLSTACK_PATH}.")

@app.route('/get-toolstack', methods=['GET'])
def get_toolstack():
    """Retrieve the contents of toolstack.json."""
    try:
        return jsonify(toolstack), 200
    except Exception as e:
        logging.error(f"Error in /get-toolstack: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/execute-task', methods=['POST'])
def execute_task():
    """Execute tasks dynamically using toolstack.json."""
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "Invalid or missing JSON payload."}), 400

        tool_name = payload.get("tool")
        task_name = payload.get("task")
        params = payload.get("params", {})

        if not tool_name or not task_name:
            return jsonify({"error": "Payload must include 'tool' and 'task' fields."}), 400

        tool_config = toolstack.get(tool_name)
        if not tool_config:
            return jsonify({"error": f"Tool '{tool_name}' not found in toolstack.json."}), 400

        task_config = tool_config["tasks"].get(task_name)
        if not task_config:
            return jsonify({"error": f"Task '{task_name}' not found for tool '{tool_name}'."}), 400

        # Simulate task execution (for now)
        logging.info(f"Executing task: {task_name} for tool: {tool_name} with params: {params}")
        return jsonify({"status": "success", "message": f"Task '{task_name}' executed successfully."}), 200

    except Exception as e:
        logging.error(f"Error in /execute-task: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
