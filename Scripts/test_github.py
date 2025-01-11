import subprocess
import json

def run_test():
    """Run a full GitHub task workflow."""
    tasks = [
        {
            "task": "force_apply_changes",
            "params": {
                "path": "test_file.py",
                "content": "print('Testing end-to-end workflow!')"
            }
        },
        {"task": "git_add", "params": {"path": "test_file.py"}},
        {"task": "commit_changes", "params": {"message": "Add test_file.py via end-to-end test"}},
        {"task": "push_changes", "params": {}},
    ]

    for task in tasks:
        result = subprocess.run(
            ["python", "github_manager.py", json.dumps(task)],
            capture_output=True,
            text=True
        )
        print(f"Task: {task['task']} - Result: {result.stdout.strip() or result.stderr.strip()}")

if __name__ == "__main__":
    run_test()