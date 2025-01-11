
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