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
    """Execute Git tasks directly in Flask."""
    data = request.json
    tool = data.get("tool")
    task = data.get("task")
    params = data.get("params", {})

    # Load toolstack
    toolstack = load_toolstack()
    if tool not in toolstack:
        return jsonify({"error": f"Tool '{tool}' not found in toolstack."}), 400

    if tool == "github":
        repo_path = "/Users/srinivas/orchestrate-rebuild/"  # Path to the Git repository

        if task == "commit_changes":
            # Check if there are changes to commit
            try:
                status = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                if not status.stdout.strip():
                    return jsonify({"status": "error", "message": "Nothing to commit"}), 400

                # Commit changes
                message = params.get("message", "Default commit message")
                subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
                subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True)
                return jsonify({"status": "success", "message": f"Committed changes with message: '{message}'"})
            except subprocess.CalledProcessError as e:
                return jsonify({"status": "error", "message": f"Git commit failed: {e.stderr}"}), 500

        elif task == "push_changes":
            # Push changes
            try:
                subprocess.run(["git", "push"], cwd=repo_path, check=True)
                return jsonify({"status": "success", "message": "Changes pushed to remote repository"})
            except subprocess.CalledProcessError as e:
                return jsonify({"status": "error", "message": f"Git push failed: {e.stderr}"}), 500

        elif task == "pull_changes":
            # Pull changes
            try:
                subprocess.run(["git", "pull"], cwd=repo_path, check=True)
                return jsonify({"status": "success", "message": "Latest changes pulled from remote repository"})
            except subprocess.CalledProcessError as e:
                return jsonify({"status": "error", "message": f"Git pull failed: {e.stderr}"}), 500

        else:
            return jsonify({"status": "error", "message": f"Unsupported GitHub task: {task}"}), 400

    return jsonify({"error": f"Unsupported tool '{tool}'."}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)