import subprocess
import sys
import json
import os

# Define the correct Git repository path
REPO_PATH = "/Users/srinivas/orchestrate-rebuild/"

def git_add(path="."):
    """Stage specific files or all files."""
    try:
        subprocess.run(["git", "add", path], cwd=REPO_PATH, check=True)
        return {"status": "success", "message": f"Files staged: {path}"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Git add failed: {str(e)}"}

def git_status():
    """Check for uncommitted changes."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"], cwd=REPO_PATH, capture_output=True, text=True, check=True
        )
        if result.stdout.strip():
            return {"status": "success", "changes": result.stdout.strip()}
        return {"status": "success", "message": "No changes to commit"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Failed to check status: {str(e)}"}

def git_reset(path="."):
    """Unstage specific files or all files."""
    try:
        subprocess.run(["git", "reset", path], cwd=REPO_PATH, check=True)
        return {"status": "success", "message": f"Files unstaged: {path}"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Git reset failed: {str(e)}"}

def check_uncommitted_changes():
    """Check if there are uncommitted changes."""
    status = git_status()
    if status.get("status") == "success" and "changes" in status:
        return True
    return False

def commit_changes(message):
    """Commit staged changes to the repository."""
    try:
        if not check_uncommitted_changes():
            return {"status": "error", "message": "Nothing to commit"}
        
        subprocess.run(["git", "commit", "-m", message], cwd=REPO_PATH, check=True)
        return {"status": "success", "message": f"Committed changes with message: '{message}'"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Git commit failed: {str(e)}"}

def push_changes():
    """Push committed changes to the remote repository."""
    try:
        subprocess.run(["git", "push"], cwd=REPO_PATH, check=True)
        return {"status": "success", "message": "Changes pushed to remote repository"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Git push failed: {str(e)}"}

def pull_changes():
    """Pull the latest changes from the remote repository."""
    try:
        subprocess.run(["git", "pull"], cwd=REPO_PATH, check=True)
        return {"status": "success", "message": "Latest changes pulled from remote repository"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Git pull failed: {str(e)}"}

def full_workflow(message):
    """Execute a full workflow: commit, then push."""
    commit_result = commit_changes(message)
    if commit_result["status"] != "success":
        return commit_result
    return push_changes()

def main():
    """Process input and execute GitHub tasks."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No payload provided"}))
        sys.exit(1)

    try:
        payload = json.loads(sys.argv[1])
        task = payload.get("task")
        params = payload.get("params", {})

        if task == "git_add":
            result = git_add(params.get("path", "."))
        elif task == "git_status":
            result = git_status()
        elif task == "git_reset":
            result = git_reset(params.get("path", "."))
        elif task == "commit_changes":
            result = commit_changes(params.get("message", "Default commit message"))
        elif task == "push_changes":
            result = push_changes()
        elif task == "pull_changes":
            result = pull_changes()
        elif task == "full_workflow":
            result = full_workflow(params.get("message", "Default commit message"))
        else:
            result = {"status": "error", "message": f"Unsupported task: {task}"}

        print(json.dumps(result))  # Always return valid JSON
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()