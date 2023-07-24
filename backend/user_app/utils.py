from datetime import datetime, timedelta
from secrets import choice, token_hex
from pytz import timezone
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

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
        if not user:
            logger.warn(f'Invalid argument(s) NULL `user` passed.')
            return None
        if not isinstance(user, User):
            logger.warn(f'Invalid argument(s) `user` passed.')
            return None
        
        if not user in User.objects.all():
            logger.warn(f'Invalid argument(s) `user` does not exist.')
            return None
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


class UserTokenUtils:
    """
    Utilities to create secure tokens for users.
    """
    LETTERS = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
               "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
    NUMBERS = tuple(str(i) for i in range(0, 10))

    TOKEN_SIZE: int = 32
    UUID_LENGTH: int = 36 #(prithoo): The length of a typical UUIDv4 value.
    SALT_01_SIZE: int = settings.SALT_01_SIZE
    SALT_02_SIZE: int = settings.SALT_02_SIZE

    @classmethod
    def generate_hex_token(cls, token_size: int = None) -> str:
        if not token_size:
            token_size = cls.TOKEN_SIZE

        return f"{token_hex(token_size).upper()}"
    
    @classmethod
    def process_user_salt(cls, user:User) -> str:
        if not user or not isinstance(user, User):
            logger.warn(
                f"Invalid argument(s) `user` passed.")
            return None

        return f"{token_hex(cls.SALT_01_SIZE)}{user.id}{token_hex(cls.SALT_02_SIZE)}"
    
    @classmethod
    def create_permanent_token(cls, usr:User) -> str:
        return f"{cls.process_user_salt(usr)}{cls.generate_hex_token()}"
    
    @classmethod
    def split_parts(cls, token:str):
        if not token or token == "":
            logger.warn(f"Invalid argument(s) `token` passed.")
            return None, None
        user_part = token[0:((cls.SALT_01_SIZE*2)+cls.UUID_LENGTH+(cls.SALT_02_SIZE*2)+1):]
        token_part = token.replace(user_part, "")

        return user_part, token_part
    
    @classmethod
    def get_user_id(cls, user_part:str=None, token:str=None)->str:
        if token and not user_part:
            user_part,_ = cls.split_parts(token)
        salt_01 = user_part[0:cls.SALT_01_SIZE*2]
        salt_02 = user_part[0-cls.SALT_02_SIZE*2-1:]

        return user_part.replace(salt_01, "").replace(salt_02, "")
