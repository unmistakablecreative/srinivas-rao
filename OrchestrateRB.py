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
    """Directly execute GitHub tasks within Flask."""
    data = request.json
    tool = data.get("tool")
    task = data.get("task")
    params = data.get("params", {})

    # Load toolstack
    toolstack = load_toolstack()
    if tool not in toolstack:
        return jsonify({"error": f"Tool '{tool}' not found in toolstack."}), 400

    if tool == "github":
        if task == "commit_changes":
            message = params.get("message", "Default commit message")
            try:
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-m", message], check=True)
                return jsonify({"status": "success", "message": f"Committed changes with message: '{message}'"})
            except subprocess.CalledProcessError as e:
                return jsonify({"status": "error", "message": f"Git commit failed: {e.stderr}"}), 500

        elif task == "push_changes":
            try:
                subprocess.run(["git", "push"], check=True)
                return jsonify({"status": "success", "message": "Changes pushed to remote repository"})
            except subprocess.CalledProcessError as e:
                return jsonify({"status": "error", "message": f"Git push failed: {e.stderr}"}), 500

        elif task == "pull_changes":
            try:
                subprocess.run(["git", "pull"], check=True)
                return jsonify({"status": "success", "message": "Latest changes pulled from remote repository"})
            except subprocess.CalledProcessError as e:
                return jsonify({"status": "error", "message": f"Git pull failed: {e.stderr}"}), 500

        else:
            return jsonify({"status": "error", "message": f"Unsupported GitHub task: {task}"}), 400

    return jsonify({"error": f"Unsupported tool '{tool}'."}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)