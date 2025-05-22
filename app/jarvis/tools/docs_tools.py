"""
Google Docs tools.
"""

from app.jarvis.tools.google_utils import get_google_service
from googleapiclient.errors import HttpError

def create_google_doc(title: str) -> dict:
    """
    Create a new Google Document.

    Args:
        title (str): The title for the new document.

    Returns:
        dict: A dictionary containing the new document's ID and URL or an error message.
              Example: {"document_id": "...", "url": "https://docs.google.com/document/d/.../edit"}
                       or {"error": "Authentication failed. Please run setup_google_auth.py"}
    """
    service = get_google_service('docs', 'v1')
    if not service:
        return {"error": "Authentication failed. Please run setup_google_auth.py"}

    try:
        doc_body = {'title': title}
        document = service.documents().create(body=doc_body).execute()
        doc_id = document.get('documentId')
        return {
            "document_id": doc_id,
            "url": f"https://docs.google.com/document/d/{doc_id}/edit"
        }
    except HttpError as e:
        return {"error": f"An API error occurred: {e.resp.reason}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def append_to_google_doc(document_id: str, text: str) -> dict:
    """
    Append text to an existing Google Document.

    Args:
        document_id (str): The ID of the document to append to.
        text (str): The text to append.

    Returns:
        dict: A dictionary indicating success or an error message.
              Example: {"status": "success", "document_id": "..."}
                       or {"error": "Authentication failed. Please run setup_google_auth.py"}
    """
    service = get_google_service('docs', 'v1')
    if not service:
        return {"error": "Authentication failed. Please run setup_google_auth.py"}

    try:
        requests = [
            {
                'insertText': {
                    'location': {
                        'segmentId': '',  # Empty string for main body
                        # By not specifying an index, text will be inserted at the end of the segment.
                        # For the body segment, this means at the end of the document.
                    },
                    'text': text + '\n'  # Add a newline for better formatting
                }
            }
        ]
        service.documents().batchUpdate(
            documentId=document_id, body={'requests': requests}
        ).execute()
        return {"status": "success", "document_id": document_id}
    except HttpError as e:
        error_message = e.resp.reason
        try:
            # Attempt to get more detailed error
            error_details = e.content.decode()
            import json
            error_json = json.loads(error_details)
            if "error" in error_json and "message" in error_json["error"]:
                error_message = error_json["error"]["message"]
        except:
            pass # Fallback to reason if details are not available
        return {"error": f"An API error occurred: {error_message}", "document_id": document_id}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}", "document_id": document_id}

def read_google_doc(document_id: str) -> dict:
    """
    Read the content of a Google Document.

    Args:
        document_id (str): The ID of the document to read.

    Returns:
        dict: A dictionary containing the document's content or an error message.
              Example: {"document_id": "...", "content": "..."}
                       or {"error": "Authentication failed. Please run setup_google_auth.py"}
    """
    service = get_google_service('docs', 'v1')
    if not service:
        return {"error": "Authentication failed. Please run setup_google_auth.py"}

    try:
        # Request only the body content, specifically paragraph elements with text runs
        document = service.documents().get(
            documentId=document_id,
            fields='body(content(paragraph(elements(textRun(content)))))'
        ).execute()
        
        doc_content = document.get('body', {}).get('content', [])
        
        full_text = ""
        for element in doc_content:
            if 'paragraph' in element:
                paragraph_elements = element.get('paragraph', {}).get('elements', [])
                for para_element in paragraph_elements:
                    if 'textRun' in para_element:
                        full_text += para_element.get('textRun', {}).get('content', '')
        
        return {"document_id": document_id, "content": full_text}
    except HttpError as e:
        error_message = e.resp.reason
        try:
            # Attempt to get more detailed error
            error_details = e.content.decode()
            import json
            error_json = json.loads(error_details)
            if "error" in error_json and "message" in error_json["error"]:
                error_message = error_json["error"]["message"]
        except:
            pass # Fallback to reason if details are not available
        return {"error": f"An API error occurred: {error_message}", "document_id": document_id}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}", "document_id": document_id}
