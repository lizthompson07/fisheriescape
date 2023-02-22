import base64

import pyotp
import six
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(user.is_active)
        )


account_activation_token = TokenGenerator()


class OTPTokenGenerator:
    """
    Sought inspiration here (DJF):
    https://medium.com/analytics-vidhya/how-to-implement-otp-based-authentication-on-django-rest-framework-185ae8032f07
    """
    secret = None

    def __init__(self):
        self.secret = self.secret or settings.SECRET_KEY

    def make_token(self, user):
        key = base64.b32encode(self._make_hash_value(user).encode())
        OTP = pyotp.HOTP(key)
        return OTP.at(user.pk)

    def check_token(self, user, token):
        if not (user and token):
            return False
        key = base64.b32encode(self._make_hash_value(user).encode())
        OTP = pyotp.HOTP(key)  # HOTP Model
        if OTP.verify(token, user.pk):  # Verifying the OTP
            return True
        return False

    def _make_hash_value(self, user):
        login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
        email_field = user.get_email_field_name()
        email = getattr(user, email_field, '') or ''
        n = timezone.now()
        timestamp = n.year + n.month + n.day
        return f'{user.pk}{user.password}{login_timestamp}{email}{self.secret}{timestamp}'


otp_token_generator = OTPTokenGenerator()
