import os
import sys
import json
import subprocess

# Define repository path
REPO_PATH = "/Users/srinivas/orchestrate-rebuild/"

def run_git_command(command):
    """Run a git command in the repository directory."""
    try:
        result = subprocess.run(
            command, cwd=REPO_PATH, capture_output=True, text=True, check=True
        )
        return {"status": "success", "output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": e.stderr.strip()}

def force_apply_changes(params):
    """Overwrite or create a file with specified content."""
    path = params.get("path")
    content = params.get("content")
    if not path or not content:
        return {"status": "error", "message": "Path and content are required for force_apply_changes"}

    full_path = os.path.join(REPO_PATH, path)
    try:
        with open(full_path, "w") as file:
            file.write(content)
        return {"status": "success", "message": f"File '{path}' updated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def git_add(params):
    """Stage specific files or all files."""
    path = params.get("path", ".")
    return run_git_command(["git", "add", path])

def git_status():
    """Check for uncommitted changes."""
    return run_git_command(["git", "status", "--porcelain"])

def git_reset(params):
    """Unstage specific files or all files."""
    path = params.get("path", ".")
    return run_git_command(["git", "reset", path])

def commit_changes(params):
    """Commit staged changes with a message."""
    message = params.get("message", "Default commit message")
    return run_git_command(["git", "commit", "-m", message])

def push_changes():
    """Push committed changes to the remote repository."""
    return run_git_command(["git", "push"])

def main():
    """Process input payload and execute GitHub tasks."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No payload provided"}))
        sys.exit(1)

    try:
        payload = json.loads(sys.argv[1])
        task = payload.get("task")
        params = payload.get("params", {})

        if task == "force_apply_changes":
            result = force_apply_changes(params)
        elif task == "git_add":
            result = git_add(params)
        elif task == "git_status":
            result = git_status()
        elif task == "git_reset":
            result = git_reset(params)
        elif task == "commit_changes":
            result = commit_changes(params)
        elif task == "push_changes":
            result = push_changes()
        else:
            result = {"status": "error", "message": f"Unsupported task: {task}"}

        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()