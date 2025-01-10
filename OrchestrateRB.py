import os
import subprocess
import logging
from flask import Flask, request, jsonify
import json  # Ensure json is imported to avoid NameError

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
        # Parse input payload
        data = request.get_json()
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

        # GitHub task execution
        if tool == "github":
            repo_path = "/Users/srinivas/orchestrate-rebuild/"  # Path to Git repository

            if task == "commit_changes":
                logging.info("Executing commit_changes task.")
                status = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                if not status.stdout.strip():
                    return jsonify({"status": "error", "message": "Nothing to commit"}), 400

                message = params.get("message", "Default commit message")
                subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
                subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True)
                return jsonify({"status": "success", "message": f"Committed changes with message: '{message}'"})

            elif task == "push_changes":
                logging.info("Executing push_changes task.")
                subprocess.run(["git", "push"], cwd=repo_path, check=True)
                return jsonify({"status": "success", "message": "Changes pushed to remote repository"})

            elif task == "force_apply_changes":
                logging.info("Executing force_apply_changes task.")
                path = params.get("path")
                content = params.get("content", "Force applied content.")
                if not path:
                    return jsonify({"status": "error", "message": "File path is required"}), 400

                full_path = os.path.join(repo_path, path)
                with open(full_path, "w") as f:
                    f.write(content)
                return jsonify({"status": "success", "message": f"File '{path}' has been updated with provided content."})

            elif task == "git_add":
                logging.info("Executing git_add task.")
                path = params.get("path", ".")
                subprocess.run(["git", "add", path], cwd=repo_path, check=True)
                return jsonify({"status": "success", "message": f"Files staged: {path}"})

            elif task == "git_status":
                logging.info("Executing git_status task.")
                status = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                if status.stdout.strip():
                    return jsonify({"status": "success", "changes": status.stdout.strip()})
                return jsonify({"status": "success", "message": "No changes to commit"})

            elif task == "git_reset":
                logging.info("Executing git_reset task.")
                path = params.get("path", ".")
                subprocess.run(["git", "reset", path], cwd=repo_path, check=True)
                return jsonify({"status": "success", "message": f"Files unstaged: {path}"})

            else:
                logging.error(f"Unsupported GitHub task: {task}")
                return jsonify({"status": "error", "message": f"Unsupported GitHub task: {task}"}), 400

        # Handle unsupported tools
        logging.error(f"Unsupported tool '{tool}'")
        return jsonify({"status": "error", "message": f"Unsupported tool '{tool}'."}), 400

    except subprocess.CalledProcessError as e:
        logging.error(f"Git command failed: {e.stderr}")
        return jsonify({"status": "error", "message": f"Git command failed: {e.stderr}"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)