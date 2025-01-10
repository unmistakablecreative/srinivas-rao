import sys
import subprocess
import json
import os

def execute_script(script_path, payload):
    """Execute a Python script with a JSON payload."""
    try:
        result = subprocess.run(
            ["python", script_path, json.dumps(payload)],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)  # Parse JSON response
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Execution failed: {e.stderr}"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Script returned invalid JSON"}

def main():
    """Process input for dynamic script execution."""
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: script_executor.py <script_path> <payload>"}))
        sys.exit(1)

    script_path = sys.argv[1]
    payload = json.loads(sys.argv[2])

    if not os.path.exists(script_path):
        print(json.dumps({"error": f"Script not found: {script_path}"}))
        sys.exit(1)

    result = execute_script(script_path, payload)
    print(json.dumps(result))

if __name__ == "__main__":
    main()