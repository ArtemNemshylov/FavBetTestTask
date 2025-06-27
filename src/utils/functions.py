"""
Utility functions
"""

from datetime import datetime


def date_to_millis(date_str: str) -> int:
    """
    Converts a date string 'YYYY.MM.DD' or 'YYYY.MM.DD HH:MM:SS' to milliseconds since epoch.

    :param date_str: Date in string format.
    :return: Integer timestamp in milliseconds.
    """

    fmt = "%Y.%m.%d %H:%M:%S" if " " in date_str else "%Y.%m.%d"
    dt = datetime.strptime(date_str, fmt)
    return int(dt.timestamp()) * 1000


def millis_to_date(ms: int) -> str:
    """
    Converts milliseconds timestamp to human-readable date string (local time).

    Args:
        ms (int): Timestamp in milliseconds.

    Returns:
        str: Formatted date string 'YYYY-MM-DD HH:MM:SS'
    """
    try:
        dt = datetime.fromtimestamp(ms / 1000)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError, OSError) as e:
        return f"Invalid timestamp: {e}"