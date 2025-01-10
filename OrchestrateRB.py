
import os
import subprocess
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TOOLSTACK_PATH = os.path.join(os.getcwd(), "Config", "toolstack.json")


def load_toolstack():
    """Load the toolstack.json file."""
    try:
        with open(TOOLSTACK_PATH, "r") as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Failed to load toolstack.json: {str(e)}")
        return {"error": "Failed to load toolstack.json"}


import json  # Add this to fix the NameError

@app.route('/get-toolstack', methods=['GET'])
def get_toolstack():
    """Retrieve the toolstack.json configuration."""
    TOOLSTACK_PATH = os.path.join(os.getcwd(), "Config", "toolstack.json")
    try:
        with open(TOOLSTACK_PATH, "r") as file:
            toolstack = json.load(file)  # This now works because json is imported
        return jsonify(toolstack), 200
    except FileNotFoundError:
        logging.error(f"Toolstack file not found at {TOOLSTACK_PATH}")
        return jsonify({"error": "Toolstack file not found"}), 500
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse toolstack.json: {str(e)}")
        return jsonify({"error": "Invalid JSON in toolstack.json"}), 500


@app.route('/execute-task', methods=['POST'])
def execute_task():
    """Execute Git tasks within Flask."""
    try:
        # Parse input
        data = request.json
        tool = data.get("tool")
        task = data.get("task")
        params = data.get("params", {})

        # Load toolstack
        toolstack = load_toolstack()
        if tool not in toolstack:
            logging.error(f"Tool '{tool}' not found in toolstack.")
            return jsonify({"error": f"Tool '{tool}' not found in toolstack."}), 400

        if tool == "github":
            repo_path = "/Users/srinivas/orchestrate-rebuild/"  # Path to Git repository

            # GitHub task: Commit changes
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
                    logging.info("Nothing to commit.")
                    return jsonify({"status": "error", "message": "Nothing to commit"}), 400

                message = params.get("message", "Default commit message")
                subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
                subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True)
                return jsonify({"status": "success", "message": f"Committed changes with message: '{message}'"})

            # GitHub task: Push changes
            elif task == "push_changes":
                logging.info("Executing push_changes task.")
                subprocess.run(["git", "push"], cwd=repo_path, check=True)
                return jsonify({"status": "success", "message": "Changes pushed to remote repository"})

            # GitHub task: Pull changes
            elif task == "pull_changes":
                logging.info("Executing pull_changes task.")
                subprocess.run(["git", "pull"], cwd=repo_path, check=True)
                return jsonify({"status": "success", "message": "Latest changes pulled from remote repository"})

            # GitHub task: Force apply changes
            elif task == "force_apply_changes":
                logging.info("Executing force_apply_changes task.")
                path = params.get("path")
                if not path:
                    return jsonify({"status": "error", "message": "File path is required for 'force_apply_changes'"}), 400

                full_path = os.path.join(repo_path, path)
                with open(full_path, "w") as f:
                    f.write("Force applied content.")
                return jsonify({"status": "success", "message": f"File '{path}' has been force-applied."})

            # GitHub task: Add files to staging
            elif task == "git_add":
                logging.info("Executing git_add task.")
                path = params.get("path", ".")
                subprocess.run(["git", "add", path], cwd=repo_path, check=True)
                return jsonify({"status": "success", "message": f"Files staged: {path}"})

            # GitHub task: Check uncommitted changes
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

            # GitHub task: Unstage files
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
        return jsonify({"error": f"Unsupported tool '{tool}'."}), 400

    # Handle Git subprocess errors
    except subprocess.CalledProcessError as e:
        logging.error(f"Git command failed: {e.stderr}")
        return jsonify({"status": "error", "message": f"Git command failed: {e.stderr}"}), 500

    # Handle unexpected errors
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



