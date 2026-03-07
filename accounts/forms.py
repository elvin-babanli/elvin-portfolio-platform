"""
Authentication forms. Production-ready validation and structure.
"""
import re
import uuid
from datetime import date
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm
from django.core.exceptions import ValidationError

from .models import UserProfile, PasswordResetVerification
from .constants import PHONE_COUNTRY_CODES


def _make_username_from_email(email):
    """Generate unique username from email."""
    base = re.sub(r"[^a-zA-Z0-9._-]", "_", email.split("@")[0])[:30]
    for _ in range(10):
        username = base if not User.objects.filter(username__iexact=base).exists() else f"{base}_{uuid.uuid4().hex[:8]}"
        if not User.objects.filter(username__iexact=username).exists():
            return username
        base = f"{base}_{uuid.uuid4().hex[:6]}"
    return f"user_{uuid.uuid4().hex[:12]}"


class LoginForm(AuthenticationForm):
    """Login: email + password."""
    username = forms.CharField(
        widget=forms.EmailInput(attrs={
            "autocomplete": "email",
            "placeholder": "Email",
            "class": "auth-input",
            "autofocus": True,
        }),
        label="",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "autocomplete": "current-password",
            "placeholder": "Password",
            "class": "auth-input",
        }),
        label="",
    )
    error_messages = {
        "invalid_login": "Invalid email or password. Please try again.",
        "inactive": "This account has been deactivated.",
    }


class RegisterForm(UserCreationForm):
    """Registration: first name, last name, email, password."""
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            "autocomplete": "given-name",
            "placeholder": "First Name",
            "class": "auth-input",
        }),
        required=True,
        max_length=150,
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            "autocomplete": "family-name",
            "placeholder": "Last Name",
            "class": "auth-input",
        }),
        required=True,
        max_length=150,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "autocomplete": "email",
            "placeholder": "Email",
            "class": "auth-input",
        }),
        required=True,
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            "placeholder": "Password",
            "class": "auth-input",
        }),
        label="",
        help_text="",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            "placeholder": "Confirm password",
            "class": "auth-input",
        }),
        label="",
        help_text="",
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return email
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = User(
            username=_make_username_from_email(self.cleaned_data["email"]),
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            is_active=True,
        )
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    error_messages = {
        "password_mismatch": "The two password fields didn't match.",
    }


class ForgotPasswordForm(forms.Form):
    """Email input for password reset request."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "autocomplete": "email",
            "placeholder": "Enter your email address",
            "class": "auth-input",
            "autofocus": True,
        }),
        label="",
    )


class VerifyCodeForm(forms.Form):
    """6-digit verification code."""
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            "autocomplete": "one-time-code",
            "placeholder": "Enter 6-digit code",
            "class": "auth-input auth-code-input",
            "inputmode": "numeric",
            "pattern": "[0-9]*",
            "maxlength": "6",
        }),
        label="",
    )

    def clean_code(self):
        code = self.cleaned_data.get("code", "").strip()
        if not code.isdigit() or len(code) != 6:
            raise ValidationError("Please enter a valid 6-digit code.")
        return code


class ResetPasswordForm(SetPasswordForm):
    """New password after code verification."""
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            "placeholder": "New password",
            "class": "auth-input",
        }),
        label="",
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            "placeholder": "Confirm new password",
            "class": "auth-input",
        }),
        label="",
    )


def _clean_phone_number(value):
    """Allow only digits. Returns empty string if invalid."""
    if not value or not isinstance(value, str):
        return ""
    digits = re.sub(r"\D", "", value)
    return digits if len(digits) <= 15 else ""


class ProfileUpdateForm(forms.ModelForm):
    """Profile: birth_date, phone (country_code + number). User fields handled separately."""
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "profile-input", "placeholder": "First name"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "profile-input", "placeholder": "Last name"}),
    )
    birth_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "profile-input profile-date-input",
            "type": "date",
            "placeholder": "DD/MM/YYYY",
        }),
    )
    phone_country_code = forms.ChoiceField(
        choices=PHONE_COUNTRY_CODES,
        required=False,
        initial="+90",
        widget=forms.Select(attrs={"class": "profile-phone-country"}),
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "profile-input profile-phone-number",
            "placeholder": "555 123 4567",
            "inputmode": "numeric",
            "pattern": "[0-9]*",
            "maxlength": "15",
        }),
    )

    class Meta:
        model = UserProfile
        fields = ("birth_date",)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            if hasattr(user, "profile") and user.profile:
                p = user.profile
                self.fields["birth_date"].initial = p.birth_date
                # Parse phone: "+901234567890" -> code="+90", number="1234567890"
                phone = (p.phone_number or "").strip()
                matched = False
                for code, _ in sorted(PHONE_COUNTRY_CODES, key=lambda x: -len(x[0])):
                    if phone.startswith(code):
                        self.fields["phone_country_code"].initial = code
                        self.fields["phone_number"].initial = _clean_phone_number(phone[len(code):])
                        matched = True
                        break
                if not matched and phone:
                    self.fields["phone_number"].initial = _clean_phone_number(phone)

    def clean_phone_number(self):
        raw = (self.cleaned_data.get("phone_number") or "").strip()
        digits = _clean_phone_number(raw)
        if raw and not digits:
            raise ValidationError("Phone number must contain only digits.")
        if len(digits) < 7 and digits:
            raise ValidationError("Phone number is too short.")
        return digits

    def clean(self):
        cleaned = super().clean()
        code = (cleaned.get("phone_country_code") or "").strip()
        num = cleaned.get("phone_number", "")
        if num:
            cleaned["phone_full"] = (code or "+90").replace(" ", "") + num
        else:
            cleaned["phone_full"] = ""
        return cleaned


class PasswordChangeForm(forms.Form):
    """Change password for logged-in user."""
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "profile-input",
            "placeholder": "Current password",
            "autocomplete": "current-password",
        }),
        label="Current password",
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "profile-input",
            "placeholder": "New password",
            "autocomplete": "new-password",
        }),
        label="New password",
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "profile-input",
            "placeholder": "Confirm new password",
            "autocomplete": "new-password",
        }),
        label="Confirm new password",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        pwd = self.cleaned_data.get("current_password")
        if not self.user.check_password(pwd):
            raise ValidationError("Current password is incorrect.")
        return pwd

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError({"new_password2": "The two password fields didn't match."})
        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()
