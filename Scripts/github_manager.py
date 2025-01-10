import subprocess
import sys
import json

def commit_changes(message):
    """Commit staged changes to the repository."""
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        return {"status": "success", "message": f"Committed changes with message: '{message}'"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Git commit failed: {str(e)}"}

def push_changes():
    """Push committed changes to the remote repository."""
    try:
        subprocess.run(["git", "push"], check=True)
        return {"status": "success", "message": "Changes pushed to remote repository"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Git push failed: {str(e)}"}

def pull_changes():
    """Pull the latest changes from the remote repository."""
    try:
        subprocess.run(["git", "pull"], check=True)
        return {"status": "success", "message": "Latest changes pulled from remote repository"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Git pull failed: {str(e)}"}

def main():
    """Process input and execute GitHub tasks."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No payload provided"}))
        sys.exit(1)

    try:
        payload = json.loads(sys.argv[1])
        task = payload.get("task")
        params = payload.get("params", {})

        if task == "commit_changes":
            result = commit_changes(params.get("message", "Default commit message"))
        elif task == "push_changes":
            result = push_changes()
        elif task == "pull_changes":
            result = pull_changes()
        else:
            result = {"status": "error", "message": f"Unsupported task: {task}"}

        print(json.dumps(result))  # Always return valid JSON
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()