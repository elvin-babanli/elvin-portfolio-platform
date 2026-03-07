"""
Authentication and user profile models.
Production-ready structure: UserProfile, PasswordResetVerification.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
import random
import string


def _generate_verification_code():
    """Generate a 6-digit numeric verification code."""
    return "".join(random.choices(string.digits, k=6))


class UserProfile(models.Model):
    """
    Extended user profile. Auth (User) separate from profile data.
    birth_date: DD/MM/YYYY display; stored as date.
    phone_number: full intl format e.g. +901234567890 (country_code + digits).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)  # e.g. +901234567890

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"Profile of {self.user.email}"


class PasswordResetVerification(models.Model):
    """
    6-digit verification code for password reset flow.
    Valid for 1 minute. User can request new code when expired.
    """
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6, default=_generate_verification_code)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "password_reset_verifications"
        verbose_name = "Password Reset Verification"
        verbose_name_plural = "Password Reset Verifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} @ {self.created_at}"

    @property
    def is_expired(self):
        """Code expires after 60 seconds."""
        return (timezone.now() - self.created_at).total_seconds() > 60

    @staticmethod
    def generate_code_for_email(email):
        """Invalidate old codes for this email and create a new one."""
        PasswordResetVerification.objects.filter(email__iexact=email).delete()
        return PasswordResetVerification.objects.create(email=email)
