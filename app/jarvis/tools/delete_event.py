"""
Delete event tool for Google Calendar integration.
"""

from .google_utils import get_google_service


def delete_event(
    event_id: str,
    confirm: bool,
) -> dict:
    """
    Delete an event from Google Calendar.

    Args:
        event_id (str): The unique ID of the event to delete
        confirm (bool): Confirmation flag (must be set to True to delete)

    Returns:
        dict: Operation status and details
    """
    # Safety check - require explicit confirmation
    if not confirm:
        return {
            "status": "error",
            "message": "Please confirm deletion by setting confirm=True",
        }

    try:
        # Get calendar service
        service = get_google_service("calendar", "v3")
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Google Calendar. Please run setup_google_auth.py or check credentials.",
            }

        # Always use primary calendar
        calendar_id = "primary"

        # Call the Calendar API to delete the event
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

        return {
            "status": "success",
            "message": f"Event {event_id} has been deleted successfully",
            "event_id": event_id,
        }

    except Exception as e:
        return {"status": "error", "message": f"Error deleting event: {str(e)}"}
