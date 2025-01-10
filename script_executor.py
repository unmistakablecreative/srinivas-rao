import json
import subprocess
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def execute_task(payload):
    """Execute tasks based on the payload."""
    try:
        tool = payload.get("tool")
        task = payload.get("task")
        params = payload.get("params", {})

        if tool == "github":
            repo_path = "/Users/srinivas/orchestrate-rebuild/"

            if task == "force_apply_changes":
                path = params.get("path")
                content = params.get("content", "Force applied content.")
                if not path:
                    return {"status": "error", "message": "File path is required"}

                full_path = os.path.join(repo_path, path)
                with open(full_path, "w") as f:
                    f.write(content)
                return {"status": "success", "message": f"File '{path}' has been updated with provided content."}

            elif task == "git_add":
                path = params.get("path", ".")
                subprocess.run(["git", "add", path], cwd=repo_path, check=True)
                return {"status": "success", "message": f"Files staged: {path}"}

            elif task == "commit_changes":
                message = params.get("message", "Default commit message")
                subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True)
                return {"status": "success", "message": f"Committed changes with message: '{message}'"}

            elif task == "push_changes":
                subprocess.run(["git", "push"], cwd=repo_path, check=True)
                return {"status": "success", "message": "Changes pushed to remote repository"}

        return {"status": "error", "message": f"Unsupported tool or task: {tool}/{task}"}
    except subprocess.CalledProcessError as e:
        logging.error(f"Git command failed: {e.stderr}")
        return {"status": "error", "message": f"Git command failed: {e.stderr}"}
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No payload provided"}))
        sys.exit(1)

    payload = json.loads(sys.argv[1])
    result = execute_task(payload)
    print(json.dumps(result))