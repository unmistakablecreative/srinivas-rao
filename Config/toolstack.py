import sys
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Define the toolstack.json path relative to the current script
TOOLSTACK_PATH = os.path.join(os.path.dirname(__file__), "toolstack.json")


def load_toolstack():
    """Load the toolstack.json file."""
    try:
        with open(TOOLSTACK_PATH, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"Toolstack file not found at {TOOLSTACK_PATH}.")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse toolstack.json: {e}")
        return {}


def save_toolstack(toolstack):
    """Save the updated toolstack.json file."""
    try:
        with open(TOOLSTACK_PATH, "w") as file:
            json.dump(toolstack, file, indent=4)
        logging.info("Toolstack successfully updated.")
    except Exception as e:
        logging.error(f"Failed to save toolstack.json: {e}")


def add_tool(params):
    """Add a new tool to the toolstack."""
    tool_name = params.get("tool_name")
    tool_config = params.get("tool_config")

    if not tool_name or not tool_config:
        return {"error": "Missing 'tool_name' or 'tool_config' in params."}

    toolstack = load_toolstack()

    if tool_name in toolstack:
        return {"error": f"Tool '{tool_name}' already exists in toolstack.json."}

    toolstack[tool_name] = tool_config
    save_toolstack(toolstack)

    return {"status": "success", "message": f"Tool '{tool_name}' added successfully."}


def remove_tool(params):
    """Remove a tool from the toolstack."""
    tool_name = params.get("tool_name")

    if not tool_name:
        return {"error": "Missing 'tool_name' in params."}

    toolstack = load_toolstack()

    if tool_name not in toolstack:
        return {"error": f"Tool '{tool_name}' does not exist in toolstack.json."}

    del toolstack[tool_name]
    save_toolstack(toolstack)

    return {"status": "success", "message": f"Tool '{tool_name}' removed successfully."}


def update_tool(params):
    """Update an existing tool in the toolstack."""
    tool_name = params.get("tool_name")
    updated_config = params.get("updated_config")

    if not tool_name or not updated_config:
        return {"error": "Missing 'tool_name' or 'updated_config' in params."}

    toolstack = load_toolstack()

    if tool_name not in toolstack:
        return {"error": f"Tool '{tool_name}' does not exist in toolstack.json."}

    # Merge the updated configuration with the existing tool configuration
    toolstack[tool_name].update(updated_config)
    save_toolstack(toolstack)

    return {"status": "success", "message": f"Tool '{tool_name}' updated successfully."}


def handle_payload(payload):
    """Process the payload and route to the correct task."""
    tool = payload.get("tool")
    task = payload.get("task")
    params = payload.get("params", {})

    if tool != "toolstack":
        return {"error": f"Unsupported tool '{tool}' in payload."}

    if task == "add_tool":
        return add_tool(params)
    elif task == "remove_tool":
        return remove_tool(params)
    elif task == "update_tool":
        return update_tool(params)

    return {"error": f"Unsupported task '{task}' for tool '{tool}'."}


def main():
    """Main function to process the input payload."""
    if len(sys.argv) < 2:
        logging.error("Usage: toolstack.py '<payload>'")
        print(json.dumps({"error": "No payload provided."}))
        sys.exit(1)

    try:
        payload = json.loads(sys.argv[1])
        logging.info(f"Received payload: {json.dumps(payload, indent=2)}")
        result = handle_payload(payload)
        print(json.dumps(result, indent=2))
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse input payload: {e}")
        print(json.dumps({"error": "Invalid JSON payload."}))
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(json.dumps({"error": str(e)}))


if __name__ == "__main__":
    main()