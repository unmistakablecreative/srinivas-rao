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
        # Log and parse input payload
        raw_data = request.data.decode('utf-8')
        logging.info(f"Raw payload: {raw_data}")
        data = request.get_json()
        logging.info(f"Parsed JSON payload: {data}")
        if not data:
            return jsonify({"status": "error", "message": "Invalid or missing payload"}), 400

        # Extract task details
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
            try:
                with open(full_path, "w") as f:
                    f.write(content)
                logging.info(f"File '{path}' updated successfully.")
                return jsonify({"status": "success", "message": f"File '{path}' has been updated with provided content."})
            except Exception as e:
                logging.error(f"Failed to write to file '{path}': {str(e)}")
                return jsonify({"status": "error", "message": f"Failed to write to file '{path}': {str(e)}"}), 500

        elif task == "git_add":
            logging.info("Executing git_add task.")
            path = params.get("path", ".")
            full_path = os.path.join(repo_path, path)
            if not os.path.exists(full_path):
                logging.error(f"File or path '{path}' does not exist.")
                return jsonify({"status": "error", "message": f"File or path '{path}' does not exist."}), 400
            subprocess.run(["git", "add", path], cwd=repo_path, check=True)
            return jsonify({"status": "success", "message": f"Files staged: {path}"})

        elif task == "commit_changes":
            logging.info("Executing commit_changes task.")
            message = params.get("message", "Default commit message")
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True)
            return jsonify({"status": "success", "message": f"Committed changes with message: '{message}'"})

        elif task == "git_push":
            logging.info("Executing git_push task.")
            subprocess.run(["git", "push"], cwd=repo_path, check=True)
            return jsonify({"status": "success", "message": "Changes pushed to remote repository"})

        elif task == "git_status":
            logging.info("Executing git_status task.")
            result = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True)
            if result.stdout.strip():
                return jsonify({"status": "success", "changes": result.stdout.strip()})
            return jsonify({"status": "success", "message": "No changes to commit"})

        elif task == "git_reset":
            logging.info("Executing git_reset task.")
            path = params.get("path", ".")
            subprocess.run(["git", "reset", path], cwd=repo_path, check=True)
            return jsonify({"status": "success", "message": f"Files unstaged: {path}"})

        elif task == "rollback_changes":
            logging.info("Executing rollback_changes task.")
            commit_id = params.get("commit_id")
            if not commit_id:
                return jsonify({"status": "error", "message": "commit_id is required"}), 400
            subprocess.run(["git", "reset", "--hard", commit_id], cwd=repo_path, check=True)
            return jsonify({"status": "success", "message": f"Rolled back to commit: {commit_id}"})

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