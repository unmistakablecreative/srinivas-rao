import json
import requests
import os

# Configuration
CONFIG_PATH = "/Users/srinivas/Dropbox/1. Projects/Orchestrate/Orchestrate Modular/Config/toolstack.json"
TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"
APP_KEY = "r6km32a6dey795z"  # Your Dropbox App Key
APP_SECRET = "nybqcp83mviq76e"  # Your Dropbox App Secret

def refresh_access_token():
    """
    Refresh the Dropbox access token using the refresh token.
    """
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

    except Exception as e:
        print(f"Error refreshing access token: {e}")

if __name__ == "__main__":
    refresh_access_token()