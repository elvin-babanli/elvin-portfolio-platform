"""
Email constants. Single source of truth for brand and sender.
Envelope sender (MAIL FROM) must match EMAIL_HOST_USER to avoid 550 relay denied.
"""
from django.conf import settings

# Brand
BRAND_NAME = "B Labs"
DOMAIN = "elvin-babanli.com"


def get_from_email():
    """
    From address for MAIL FROM. Must exactly match EMAIL_HOST_USER (auth user)
    to avoid 550 "Mail relay denied" from Google Workspace.
    """
    auth_user = getattr(settings, "EMAIL_HOST_USER", "") or ""
    if auth_user:
        return f"{BRAND_NAME} <{auth_user}>"
    default = getattr(settings, "DEFAULT_FROM_EMAIL", "") or f"{BRAND_NAME} <updates@{DOMAIN}>"
    return default
