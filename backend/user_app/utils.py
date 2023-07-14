from datetime import datetime, timedelta
from secrets import choice, token_hex
from pytz import timezone

from django.conf import settings
from django.contrib.auth.hashers import make_password

from rest_framework_simplejwt.tokens import RefreshToken

from user_app.models import User, UserLoginOTP
from user_app.serializers import UserLoginOTPInputSerializer

from user_app import logger


class JWTUtils:
    """
    Utilities for basic operation on JWT.
    """
    @classmethod
    def get_tokens_for_user(cls, user: User = None):
        refresh = RefreshToken.for_user(user)

        return {
            'refreshToken': str(refresh),
            'accessToken': str(refresh.access_token),
        }


class LoginOTPUtils:
    """
    Utilities for creation and management of login OTPs for users.
    """
    LETTERS = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
               "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
    NUMBERS = tuple(str(i) for i in range(0, 10))

    OTP_SIZE: int = 6
    OTP_EXPIRY_MINUTES: int = 5

    @classmethod
    def generate_text_otp(cls, otp_size: int = None) -> str:
        if not otp_size:
            otp_size = cls.OTP_SIZE

        return f"{''.join(choice(cls.LETTERS) for _ in range(otp_size))}"

    @classmethod
    def generate_numeric_otp(cls, otp_size: int = None) -> str:
        if not otp_size:
            otp_size = cls.OTP_SIZE

        return ''.join(choice(cls.NUMBERS) for _ in range(otp_size))

    @classmethod
    def generate_hex_otp(cls, otp_size: int = None) -> str:
        if not otp_size:
            otp_size = cls.OTP_SIZE

        return f"{token_hex(otp_size//2)}".upper()

    @classmethod
    def assign_otp_to_user(cls, user: User, otp:str) -> UserLoginOTP:

        if not user or not isinstance(user, User):
            logger.warning(
                f"Invalid argument(s) `user` passed.")
            return None
        
        if not otp or not isinstance(otp, str) or otp == "":
            logger.warning(
                f"Invalid argument(s) `otp` passed.")
            return None

        data = {
            "user": f"{user.id}",
            "otp": make_password(otp),
            "otp_expires_at": datetime.now(timezone(settings.TIME_ZONE)) + timedelta(minutes=cls.OTP_EXPIRY_MINUTES)
        }

        deserialized = UserLoginOTPInputSerializer(data=data)
        if not deserialized.is_valid():
            logger.exception(f"Error: {deserialized.errors}")
            return None

        deserialized.save()
        return deserialized.instance
