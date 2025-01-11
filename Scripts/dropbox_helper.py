import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = "/Users/srinivas/orchestrate-rebuild/Config/.env"
load_dotenv(dotenv_path)

# Dropbox API configuration
DROPBOX_TOKEN = os.getenv("DROPBOX_OAUTH_TOKEN")
TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"
APP_KEY = os.getenv("DROPBOX_APP_KEY")
APP_SECRET = os.getenv("DROPBOX_APP_SECRET")

# Path to toolstack.json for fallback
CONFIG_PATH = "/Users/srinivas/orchestrate-rebuild/Config/toolstack.json"

def refresh_access_token():
    """Refresh the Dropbox access token using the refresh token."""
    try:
        # Load the current refresh token from the toolstack
        with open(CONFIG_PATH, "r") as file:
            config = json.load(file)
        refresh_token = config["dropbox"]["credentials"].get("refresh_token")

        if not refresh_token:
            raise ValueError("Refresh token not found in toolstack.json.")

        # Request a new access token
        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": APP_KEY,
                "client_secret": APP_SECRET,
            },
        )

        if response.status_code != 200:
            raise Exception(f"Failed to refresh access token: {response.text}")

        new_access_token = response.json().get("access_token")
        if not new_access_token:
            raise ValueError("New access token not found in the API response.")

        # Update toolstack.json with the new access token
        config["dropbox"]["credentials"]["oauth2_access_token"] = new_access_token
        with open(CONFIG_PATH, "w") as file:
            json.dump(config, file, indent=4)

        print("Dropbox access token refreshed and updated successfully.")
        return new_access_token

    except Exception as e:
        print(f"Error refreshing access token: {e}")
        return None

def ensure_access_token():
    """Ensure a valid Dropbox access token is available."""
    global DROPBOX_TOKEN
    if not DROPBOX_TOKEN:
        DROPBOX_TOKEN = refresh_access_token()
        if not DROPBOX_TOKEN:
            raise ValueError("Failed to obtain a valid Dropbox access token.")

def upload_file(file_path, destination_path):
    """Upload a file to Dropbox."""
    ensure_access_token()
    url = "https://content.dropboxapi.com/2/files/upload"
    headers = {
        "Authorization": f"Bearer {DROPBOX_TOKEN}",
        "Dropbox-API-Arg": json.dumps({"path": destination_path}),
        "Content-Type": "application/octet-stream",
    }

    try:
        with open(file_path, "rb") as f:
            response = requests.post(url, headers=headers, data=f)

        if response.status_code != 200:
            raise Exception(f"Failed to upload file: {response.text}")

        print(f"File uploaded successfully to {destination_path}")

    except Exception as e:
        print(f"Error uploading file: {e}")

def get_temporary_link(file_path):
    """Get a temporary link for a Dropbox file."""
    ensure_access_token()
    url = "https://api.dropboxapi.com/2/files/get_temporary_link"
    headers = {
        "Authorization": f"Bearer {DROPBOX_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {"path": file_path}

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            raise Exception(f"Failed to get temporary link: {response.text}")

        temp_link = response.json().get("link")
        print(f"Temporary link: {temp_link}")
        return temp_link

    except Exception as e:
        print(f"Error getting temporary link: {e}")

def search_file(query):
    """Search for files in Dropbox matching the query."""
    ensure_access_token()
    url = "https://api.dropboxapi.com/2/files/search_v2"
    headers = {
        "Authorization": f"Bearer {DROPBOX_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {"query": query}

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            raise Exception(f"Failed to search files: {response.text}")

        matches = response.json().get("matches", [])
        print(f"Found {len(matches)} results for query '{query}'")
        return matches

    except Exception as e:
        print(f"Error searching for files: {e}")

def get_file(file_path):
    """Get the content of a Dropbox file."""
    ensure_access_token()
    url = "https://content.dropboxapi.com/2/files/download"
    headers = {
        "Authorization": f"Bearer {DROPBOX_TOKEN}",
        "Dropbox-API-Arg": json.dumps({"path": file_path}),
    }

    try:
        response = requests.post(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get file: {response.text}")

        file_content = response.content.decode("utf-8")
        print(f"File content:\n{file_content}")
        return file_content

    except Exception as e:
        print(f"Error getting file: {e}")

if __name__ == "__main__":
    # Example usages
    upload_file("/path/to/local/file.txt", "/destination/in/dropbox/file.txt")
    get_temporary_link("/destination/in/dropbox/file.txt")
    search_file("Seth Godin")
    get_file("/destination/in/dropbox/file.txt")