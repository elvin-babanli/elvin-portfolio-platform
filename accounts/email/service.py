"""
Modular email service. Template-based, future-ready for branded HTML and images.
"""
import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def _get_from_email():
    """Use DEFAULT_FROM_EMAIL; fallback for development."""
    return getattr(
        settings,
        "DEFAULT_FROM_EMAIL",
        "noreply@localhost",
    )


def send_templated_email(
    to_emails,
    subject,
    template_name,
    context=None,
    html_template_name=None,
):
    """
    Send email from a template. Future-ready for branded HTML templates and images.

    Args:
        to_emails: list of recipient emails
        subject: email subject
        template_name: path to text/HTML template (e.g. 'accounts/emails/password_reset_code.html')
        context: dict for template rendering
        html_template_name: optional separate HTML template (if different from main)

    Returns:
        True on success, False on failure
    """
    if context is None:
        context = {}

    try:
        html_content = render_to_string(
            html_template_name or template_name,
            context,
        )
        text_content = strip_tags(html_content)
    except Exception as e:
        logger.exception("Email template render failed: %s", e)
        return False

    from_email = _get_from_email()
    if isinstance(to_emails, str):
        to_emails = [to_emails]

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=to_emails,
    )
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send(fail_silently=False)
        logger.info("Email sent to %s: %s", to_emails, subject)
        return True
    except Exception as e:
        logger.exception("Email send failed: %s", e)
        return False


def send_password_reset_code(to_email: str, code: str) -> bool:
    """
    Send password reset verification code. Uses templated email service.
    Easy to swap template later for branded HTML/images.
    """
    return send_templated_email(
        to_emails=[to_email],
        subject="Password Reset Verification Code",
        template_name="accounts/emails/password_reset_code.html",
        context={"code": code},
    )
