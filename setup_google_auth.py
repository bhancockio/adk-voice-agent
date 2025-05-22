#!/usr/bin/env python3
"""
Google Authentication Setup Script

This script helps you set up OAuth 2.0 credentials for Google services integration.
Follow the instructions in the console.
"""

import os
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

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


def setup_oauth():
    """Set up OAuth 2.0 for Google services"""
    print("\n=== Google OAuth Setup ===\n")
    print("This script will guide you through authorizing access to Google services.")
    print("If you have previously authorized, this may re-authorize and request new permissions.\n")

    if not CREDENTIALS_PATH.exists():
        print(f"Error: {CREDENTIALS_PATH} not found!")
        print("\nTo set up Google services integration:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select an existing one")
        print("3. Enable the Google Calendar API, Google Drive API, Google Docs API, and Google Sheets API")
        print("4. Create OAuth 2.0 credentials (Desktop application)")
        print(
            "5. Download the credentials and save them as 'credentials.json' in this directory"
        )
        print("\nThen run this script again.")
        return False

    print(f"Found {CREDENTIALS_PATH}. Setting up OAuth flow...")

    try:
        # Run the OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json())

        print(f"\nSuccessfully saved credentials to {TOKEN_PATH}")

        # Test the API connection
        print("\nTesting connection to Google Calendar API (as a sample)...")
        service = build("calendar", "v3", credentials=creds)
        calendar_list = service.calendarList().list().execute()
        # Check if 'items' key exists, otherwise default to empty list
        calendars = calendar_list.get("items", []) 

        if calendars:
            print(f"\nSuccess! Found {len(calendars)} calendars (sample test):")
            for calendar in calendars:
                print(f"- {calendar.get('summary', 'N/A')} ({calendar.get('id', 'N/A')})")
        else:
            print(
                "\nSuccess! Connected to Google Calendar API (sample test), but no calendars found."
            )

        print(
            "\nOAuth setup complete! You can now use the Google services integration."
        )
        return True

    except Exception as e:
        print(f"\nError during setup: {str(e)}")
        return False


if __name__ == "__main__":
    setup_oauth()
