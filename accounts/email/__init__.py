"""
Modular email service. Future-ready for HTML templates, images, branded layouts.
"""
from .service import send_templated_email, send_password_reset_code

__all__ = ["send_templated_email", "send_password_reset_code"]
