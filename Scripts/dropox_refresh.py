import requests
import webbrowser
import os
import json

# Configuration
APP_KEY = "ptg8oamzq8o9nzg"
APP_SECRET = "nybqcp83mviq76e"
AUTH_URL = "https://www.dropbox.com/oauth2/authorize"
TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"
CONFIG_PATH = "/Users/srinivas/Dropbox/1. Projects/Orchestrate/Orchestrate Modular/Config/toolstack.json"

def get_authorization_code():
    """
    Open the Dropbox OAuth page and prompt the user for the authorization code.
    """
    url = f"{AUTH_URL}?response_type=code&client_id={APP_KEY}"
    print(f"Visit this URL to authorize the app:\n{url}")
    webbrowser.open(url)
    auth_code = input("Enter the authorization code here: ").strip()
    return auth_code

def exchange_authorization_code(auth_code):
    """
    Exchange the authorization code for an access token and refresh token.
    """
    try:
        response = requests.post(
            TOKEN_URL,
            data={
                "code": auth_code,
                "grant_type": "authorization_code",
                "client_id": APP_KEY,
                "client_secret": APP_SECRET,
            },
        )
        if response.status_code != 200:
            raise Exception(f"Failed to exchange authorization code: {response.text}")
        tokens = response.json()
        return tokens.get("access_token"), tokens.get("refresh_token")
    except Exception as e:
        print(f"Error exchanging authorization code: {e}")
        return None, None

def update_toolstack(access_token, refresh_token):
    """
    Update toolstack.json with the new access and refresh tokens.
    """
    try:
        with open(CONFIG_PATH, "r") as file:
            config = json.load(file)

        # Update the tokens
        config["dropbox"]["credentials"]["oauth2_access_token"] = access_token
        config["dropbox"]["credentials"]["refresh_token"] = refresh_token

        with open(CONFIG_PATH, "w") as file:
            json.dump(config, file, indent=4)

        print("Toolstack updated with new tokens.")
    except Exception as e:
        print(f"Error updating toolstack.json: {e}")

if __name__ == "__main__":
    print("Starting Dropbox token refresh process...")
    auth_code = get_authorization_code()
    if not auth_code:
        print("Authorization code is required. Exiting.")
        exit(1)

    access_token, refresh_token = exchange_authorization_code(auth_code)
    if access_token and refresh_token:
        update_toolstack(access_token, refresh_token)
        print("Dropbox token refresh complete.")
    else:
        print("Failed to refresh tokens.")