"""
Google Sheets tools.
"""

from app.jarvis.tools.google_utils import get_google_service
from googleapiclient.errors import HttpError

def create_spreadsheet(title: str) -> dict:
    """
    Create a new Google Spreadsheet.

    Args:
        title (str): The title for the new spreadsheet.

    Returns:
        dict: A dictionary containing the new spreadsheet's ID and URL or an error message.
              Example: {"spreadsheet_id": "...", "url": "..."}
                       or {"error": "Authentication failed. Please run setup_google_auth.py"}
    """
    service = get_google_service('sheets', 'v4')
    if not service:
        return {"error": "Authentication failed. Please run setup_google_auth.py"}

    try:
        spreadsheet_body = {'properties': {'title': title}}
        spreadsheet = service.spreadsheets().create(
            body=spreadsheet_body,
            fields='spreadsheetId,spreadsheetUrl'
        ).execute()
        return {
            "spreadsheet_id": spreadsheet.get('spreadsheetId'),
            "url": spreadsheet.get('spreadsheetUrl')
        }
    except HttpError as e:
        return {"error": f"An API error occurred: {e.resp.reason}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def read_sheet_cell(spreadsheet_id: str, sheet_name: str, cell_range: str) -> dict:
    """
    Read data from a specific cell or range in a Google Spreadsheet.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet.
        sheet_name (str): The name of the sheet (e.g., "Sheet1").
        cell_range (str): The cell or range to read (e.g., "A1", "A1:B5").

    Returns:
        dict: A dictionary containing the values read or an error message.
              Example: {"spreadsheet_id": "...", "range": "Sheet1!A1", "values": [["Value"]]}
                       or {"error": "Authentication failed. Please run setup_google_auth.py"}
    """
    service = get_google_service('sheets', 'v4')
    if not service:
        return {"error": "Authentication failed. Please run setup_google_auth.py"}

    full_range = f"{sheet_name}!{cell_range}"
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=full_range
        ).execute()
        values = result.get('values', [])
        return {
            "spreadsheet_id": spreadsheet_id,
            "range": full_range,
            "values": values
        }
    except HttpError as e:
        error_message = e.resp.reason
        try:
            error_details = e.content.decode()
            import json
            error_json = json.loads(error_details)
            if "error" in error_json and "message" in error_json["error"]:
                error_message = error_json["error"]["message"]
        except:
            pass # Fallback to reason
        return {"error": f"An API error occurred: {error_message}", "spreadsheet_id": spreadsheet_id, "range_requested": full_range}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}", "spreadsheet_id": spreadsheet_id, "range_requested": full_range}

def write_to_sheet_cell(spreadsheet_id: str, sheet_name: str, cell_range: str, data: list[list[str]]) -> dict:
    """
    Write data to a specific cell or range in a Google Spreadsheet.

    Args:
        spreadsheet_id (str): The ID of the spreadsheet.
        sheet_name (str): The name of the sheet (e.g., "Sheet1").
        cell_range (str): The cell or range to write to (e.g., "A1", "A1:B2").
                          The top-left cell of the range.
        data (list[list[str]]): The data to write. Must be a list of lists,
                                 e.g., [["Hello", "World"], ["Next", "Row"]].

    Returns:
        dict: A dictionary indicating success or an error message.
              Example: {"status": "success", "spreadsheet_id": "...", "updated_range": "Sheet1!A1:B2"}
                       or {"error": "Authentication failed. Please run setup_google_auth.py"}
    """
    if not isinstance(data, list) or not all(isinstance(row, list) for row in data):
        return {"error": "Invalid data format. 'data' must be a list of lists (e.g., [['value1', 'value2']])."}

    service = get_google_service('sheets', 'v4')
    if not service:
        return {"error": "Authentication failed. Please run setup_google_auth.py"}

    full_range = f"{sheet_name}!{cell_range}"
    body = {'values': data}
    try:
        response = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=full_range,
            valueInputOption='USER_ENTERED',  # Interprets input as if typed by a user
            body=body
        ).execute()
        return {
            "status": "success",
            "spreadsheet_id": spreadsheet_id,
            "updated_range": response.get('updatedRange'),
            "updated_cells": response.get('updatedCells')
        }
    except HttpError as e:
        error_message = e.resp.reason
        try:
            error_details = e.content.decode()
            import json
            error_json = json.loads(error_details)
            if "error" in error_json and "message" in error_json["error"]:
                error_message = error_json["error"]["message"]
        except:
            pass # Fallback to reason
        return {"error": f"An API error occurred: {error_message}", "spreadsheet_id": spreadsheet_id, "range_attempted": full_range}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}", "spreadsheet_id": spreadsheet_id, "range_attempted": full_range}
