import subprocess
import sys
import json
import os

# Define the correct Git repository path
REPO_PATH = "/Users/srinivas/orchestrate-rebuild/"

def run_git_command(command, cwd=REPO_PATH):
    """Run a git command and handle errors."""
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=True)
        return {"status": "success", "output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr.strip() or str(e)}

def git_add(path="."):
    """Stage specific files or all files."""
    return run_git_command(["git", "add", path])

def git_status():
    """Check for uncommitted changes."""
    result = run_git_command(["git", "status", "--porcelain"])
    if result["status"] == "success" and result.get("output"):
        return {"status": "success", "changes": result["output"]}
    elif result["status"] == "success":
        return {"status": "success", "message": "No changes to commit"}
    return result

def git_reset(path="."):
    """Unstage specific files or all files."""
    return run_git_command(["git", "reset", path])

def check_uncommitted_changes():
    """Check if there are uncommitted changes."""
    status = git_status()
    return status.get("status") == "success" and "changes" in status

def commit_changes(message):
    """Commit staged changes to the repository."""
    if not check_uncommitted_changes():
        return {"status": "error", "message": "Nothing to commit"}
    return run_git_command(["git", "commit", "-m", message])

def push_changes():
    """Push committed changes to the remote repository."""
    return run_git_command(["git", "push"])

def pull_changes():
    """Pull the latest changes from the remote repository."""
    return run_git_command(["git", "pull"])

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

        print(json.dumps(result, indent=2))  # Improved JSON output for readability
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
