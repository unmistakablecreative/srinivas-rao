import json
import logging
import os
import subprocess
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Path to toolstack.json
TOOLSTACK_PATH = "/Users/srinivas/Dropbox/1. Projects/Orchestrate/Orchestrate Modular/Config/toolstack.json"

def load_toolstack():
    """Load the toolstack.json configuration."""
    try:
        with open(TOOLSTACK_PATH, "r") as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Error loading toolstack.json: {e}")
        return {}

def execute_task(payload):
    """Dynamically execute tasks based on the toolstack configuration."""
    try:
        tool = payload.get("tool")
        task = payload.get("task")
        params = payload.get("params", {})

        # Load toolstack
        toolstack = load_toolstack()
        if tool not in toolstack:
            return {"status": "error", "message": f"Unsupported tool: {tool}"}

        tool_config = toolstack[tool]
        if task not in tool_config.get("tasks", {}):
            return {"status": "error", "message": f"Unsupported task: {tool}/{task}"}

        # Get script path
        script_path = tool_config.get("path")
        if not script_path or not os.path.exists(script_path):
            return {"status": "error", "message": f"Script path for tool '{tool}' is invalid or missing."}

        # Execute the script
        result = subprocess.run(
            ["python", script_path, json.dumps(payload)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr.strip()}

        return json.loads(result.stdout)

    except Exception as e:
        logging.error(f"Unexpected error in script executor: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No payload provided"}))
        sys.exit(1)

    payload = json.loads(sys.argv[1])
    result = execute_task(payload)
    print(json.dumps(result))