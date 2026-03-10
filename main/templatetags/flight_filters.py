"""
Template filters for flight email display.
"""
from datetime import datetime

from django import template

register = template.Library()


@register.filter
def flight_date(s):
    """Format YYYY-MM-DD to '30 Mar 2026' (day month year)."""
    if not s or len(str(s)) < 10:
        return s
    try:
        dt = datetime.strptime(str(s)[:10], "%Y-%m-%d")
        return dt.strftime("%d %b %Y")
    except (ValueError, TypeError):
        return s
