import os
import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define scopes needed for Google services
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
]

# Path for token storage
TOKEN_PATH = Path(os.path.expanduser("~/.credentials/google_token.json"))
CREDENTIALS_PATH = Path("credentials.json")


def get_google_service(service_name: str, api_version: str):
    """Loads Google credentials and builds a service client.

    Args:
        service_name: The name of the Google service (e.g., 'calendar', 'drive').
        api_version: The API version (e.g., 'v3', 'v1').

    Returns:
        A Google API client resource object if successful, otherwise None.
    """
    creds = None
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_info(json.loads(TOKEN_PATH.read_text()), SCOPES)
        except json.JSONDecodeError:
            print(f"Error: Could not parse {TOKEN_PATH}. It might be corrupted.")
            creds = None
        except Exception as e:
            print(f"An unexpected error occurred while loading token from {TOKEN_PATH}: {e}")
            creds = None


    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
                TOKEN_PATH.write_text(creds.to_json())
                print(f"Credentials refreshed and saved to {TOKEN_PATH}")
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                creds = None  # Ensure creds is None if refresh fails
        else:
            creds = None # Ensure creds is None if not valid and cannot be refreshed

    if not creds:
        print(f"\nError: Could not load valid credentials.")
        print(f"Please run 'python setup_google_auth.py' to authorize the application.")
        return None

    try:
        service = build(service_name, api_version, credentials=creds)
        print(f"Successfully built Google {service_name} service, version {api_version}.")
        return service
    except HttpError as e:
        print(f"An API error occurred: {e}")
        if e.resp.status == 403:
            print("This might be due to insufficient permissions for the requested scopes during the initial authentication.")
            print(f"Please re-run 'python setup_google_auth.py' and ensure all listed scopes are approved.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while building the service: {e}")
        return None
