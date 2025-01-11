import json
import logging
import os
import subprocess
import sys
import tempfile

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

def execute_dynamic_script(content, language="python"):
    """Execute a dynamic script in the specified language."""
    if not content:
        return {"status": "error", "message": "No script content provided."}

    try:
        # Write the script to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{language}") as temp_file:
            temp_file.write(content.encode())
            temp_file.flush()
            script_path = temp_file.name

        # Determine execution command
        if language == "python":
            command = ["python", script_path]
        elif language == "bash":
            command = ["bash", script_path]
        elif language == "node":
            command = ["node", script_path]
        else:
            return {"status": "error", "message": f"Unsupported script language: {language}"}

        # Execute the script
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr.strip()}

        return {"status": "success", "output": result.stdout.strip()}

    finally:
        # Clean up the temporary file
        if os.path.exists(script_path):
            os.remove(script_path)

def execute_task(payload):
    """Execute tasks dynamically based on payload."""
    try:
        # Handle dynamic scripts
        if "dynamic_script" in payload:
            script_content = payload["dynamic_script"].get("content")
            script_language = payload["dynamic_script"].get("language", "python")
            return execute_dynamic_script(script_content, script_language)

        # Fallback to toolstack execution
        tool = payload.get("tool")
        task = payload.get("task")
        params = payload.get("params", {})

        logging.info(f"Received payload: {json.dumps(payload, indent=2)}")

        # Load toolstack
        toolstack = load_toolstack()
        if tool not in toolstack:
            return {"status": "error", "message": f"Unsupported tool: {tool}"}

        tool_config = toolstack[tool]
        if task not in tool_config.get("tasks", {}):
            return {"status": "error", "message": f"Unsupported task: {tool}/{task}"}

        # Get the script path for the tool
        script_path = tool_config.get("path")
        if not script_path or not os.path.exists(script_path):
            return {"status": "error", "message": f"Script path for tool '{tool}' is invalid or missing."}

        # Execute the script
        logging.info(f"Executing script: {script_path} with task: {task}")
        result = subprocess.run(
            ["python", script_path, json.dumps(payload)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr.strip()}

        return json.loads(result.stdout)

    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON payload: {e}")
        return {"status": "error", "message": f"Invalid JSON payload: {e}"}
    except Exception as e:
        logging.error(f"Unexpected error in script executor: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No payload provided."}))
        sys.exit(1)

    try:
        payload = json.loads(sys.argv[1])
        result = execute_task(payload)
        print(json.dumps(result, indent=2))
    except Exception as e:
        logging.error(f"Unexpected error in main execution: {e}")
        print(json.dumps({"status": "error", "message": str(e)}))