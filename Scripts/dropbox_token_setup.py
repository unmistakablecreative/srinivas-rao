import requests

# App credentials
APP_KEY = "r6km32a6dey795z"
APP_SECRET = "50xvo387ymagb4w"

# Authorization code
AUTHORIZATION_CODE = "Tm75E6Kc3okAAAAAAAG8xzQyVI0ECIhJkH7Bma0quhY"

def get_refresh_token():
    """Exchange the authorization code for a refresh token."""
    url = "https://api.dropboxapi.com/oauth2/token"
    data = {
        "code": AUTHORIZATION_CODE,
        "grant_type": "authorization_code",
        "client_id": APP_KEY,
        "client_secret": APP_SECRET
    }

    response = requests.post(url, data=data)
    if response.status_code == 200:
        tokens = response.json()
        refresh_token = tokens.get("refresh_token")
        access_token = tokens.get("access_token")
        print("Refresh Token:", refresh_token)
        print("Access Token:", access_token)
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    get_refresh_token()