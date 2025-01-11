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



@app.route('/execute-script', methods=['POST'])
def execute_script():
    """Execute a Python script dynamically with arguments or a payload."""
    try:
        # Parse the incoming JSON payload
        data = request.get_json()
        if not data or "script_path" not in data:
            return jsonify({"status": "error", "message": "Missing 'script_path' parameter"}), 400

        # Extract the script parameters
        script_path = data["script_path"]
        payload = data.get("payload", None)
        arguments = data.get("arguments", [])

        # Ensure the script file exists
        if not os.path.exists(script_path):
            return jsonify({"status": "error", "message": f"Script not found: {script_path}"}), 404

        # Prepare the command to execute
        args = ["python3", script_path]

        # Pass the payload as a JSON string if present
        if payload:
            args.append(json.dumps(payload))

        # Append any additional arguments as-is
        if arguments:
            for arg in arguments:
                args.append(arg)

        # Log the exact command for debugging purposes
        logging.info(f"Executing script with args: {args}")

        # Execute the script
        result = subprocess.run(args, capture_output=True, text=True)

        # Return the result
        return jsonify({
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout.strip(),
            "error": result.stderr.strip()
        }), 200 if result.returncode == 0 else 500

    except Exception as e:
        logging.error(f"Error in execute-script: {str(e)}")
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

            # Handle force_apply_changes
            if task == "force_apply_changes":
                logging.info("Executing force_apply_changes task.")
                path = params.get("path")
                content = params.get("content", "")
                if not path:
                    return jsonify({"status": "error", "message": "File path is required"}), 400

                full_path = os.path.join(repo_path, path)
                logging.info(f"Writing content to file: {full_path}")
                try:
                    with open(full_path, "w") as f:
                        f.write(content)
                    return jsonify({"status": "success", "message": f"File '{path}' has been updated with provided content."})
                except Exception as e:
                    logging.error(f"Failed to write to file '{path}': {str(e)}")
                    return jsonify({"status": "error", "message": f"Failed to write to file '{path}': {str(e)}"}), 500

            # Other Git operations
            elif task == "git_add":
                logging.info("Executing git_add task.")
                path = params.get("path", ".")
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

        # Handle unsupported tools
        logging.error(f"Unsupported tool '{tool}'")
        return jsonify({"status": "error", "message": f"Unsupported tool '{tool}'."}), 400

    except subprocess.CalledProcessError as e:
        logging.error(f"Git command failed: {e.stderr}")
        return jsonify({"status": "error", "message": f"Git command failed: {e.stderr}"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500




@app.route('/self-test', methods=['GET'])
def self_test():
    """Run self-diagnostics for the server."""
    try:
        # Check toolstack loading
        toolstack = load_toolstack()
        if "error" in toolstack:
            toolstack_status = "Toolstack failed to load"
        else:
            toolstack_status = "Toolstack loaded successfully"

        # Check endpoint status (basic ping test)
        try:
            response = app.test_client().get('/get-toolstack')
            endpoint_status = "All endpoints responding correctly" if response.status_code == 200 else "Issue with endpoints"
        except Exception as e:
            endpoint_status = f"Error testing endpoints: {str(e)}"

        # Assemble diagnostics result
        diagnostics = {
            "toolstack_status": toolstack_status,
            "endpoint_status": endpoint_status
        }

        return jsonify({"health": {"status": 200, "response": diagnostics}}), 200

    except Exception as e:
        logging.error(f"Self-test failed: {str(e)}")
        return jsonify({"health": {"status": 500, "response": str(e)}}), 500



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=False)