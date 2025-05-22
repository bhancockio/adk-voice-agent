"""
Google Drive tools.
"""

from app.jarvis.tools.google_utils import get_google_service
from googleapiclient.errors import HttpError

def list_drive_files(folder_id: str = None, query: str = None) -> dict:
    """
    List files and folders in Google Drive.

    Args:
        folder_id (str, optional): ID of the folder to list files from.
                                   If None, lists files from 'My Drive' (root).
        query (str, optional): Additional query string to filter files (e.g., "name contains 'report'").

    Returns:
        dict: A dictionary containing a list of files or an error message.
              Example: {"files": [{"id": "...", "name": "...", "type": "...", "link": "..."}]}
                       or {"error": "Authentication failed. Please run setup_google_auth.py"}
    """
    service = get_google_service('drive', 'v3')
    if not service:
        return {"error": "Authentication failed. Please run setup_google_auth.py"}

    search_conditions = []
    if folder_id:
        search_conditions.append(f"'{folder_id}' in parents")
    else:
        # If no folder_id is specified, we can implicitly list from 'My Drive'
        # by not adding any parent condition, or explicitly target 'root'
        # For clarity and to avoid potential issues with shared files appearing at top level,
        # it's often better to be explicit if "My Drive" is the specific target.
        # However, the API's default behavior without a parent constraint is usually listing
        # items in "My Drive" that the user owns or has direct access to at the root level.
        # For this implementation, we'll let the absence of a folder_id imply listing from the default view (usually My Drive).
        pass

    if query:
        search_conditions.append(query)
    
    # Ensure files that are trashed are not listed
    search_conditions.append("trashed = false")

    search_query = " and ".join(search_conditions) if search_conditions else None
    
    print(f"Executing Drive search with query: '{search_query}'")

    try:
        results = service.files().list(
            q=search_query,
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType, webViewLink)"
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            return {"files": [], "message": "No files found matching your criteria."}

        formatted_files = []
        for item in items:
            formatted_files.append({
                "id": item.get('id'),
                "name": item.get('name'),
                "type": item.get('mimeType'),
                "link": item.get('webViewLink')
            })
        
        return {"files": formatted_files}

    except HttpError as e:
        error_content = e.resp.reason
        try:
            # Attempt to parse more detailed error from the response content
            error_details = e.content.decode()
            import json
            error_json = json.loads(error_details)
            if "error" in error_json and "message" in error_json["error"]:
                error_content = error_json["error"]["message"]
        except:
            pass # Stick with e.resp.reason if parsing fails
        return {"error": f"An API error occurred: {error_content}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
