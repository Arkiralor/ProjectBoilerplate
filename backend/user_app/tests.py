from jose import jwt
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.test import TestCase
from django.utils import timezone

from user_app.models import User, UserLoginOTP
from user_app.utils import JWTUtils, LoginOTPUtils, UserTokenUtils

from user_app import logger


class JWTUtilsTestCase(TestCase):

    def setUp(self):
        data = {
            "username": "test.user.001",
            "password": "R4nd0mPa$$word",
            "email": "test.user.001@email.com"
        }
        try:
            self.user, _ = User.objects.get_or_create(**data)
        except Exception as ex:
            logger.warning(f"{ex}")

        tokens = JWTUtils.get_tokens_for_user(self.user)
        self.accessToken = tokens['accessToken']
        self.refreshToken = tokens['refreshToken']
        self.access_decoded = jwt.decode(token=self.accessToken, key=settings.SECRET_KEY, algorithms=[
            settings.SIMPLE_JWT.get('ALGORITHM'),])
        self.refresh_decoded = jwt.decode(token=self.refreshToken, key=settings.SECRET_KEY, algorithms=[
            settings.SIMPLE_JWT.get('ALGORITHM'),])

    def test_get_tokens_for_user_returns_tokens(self):
        self.assertIsInstance(self.accessToken, str)
        self.assertIsInstance(self.refreshToken, str)

    def test_access_token_validity(self):
        access = self.access_decoded
        self.assertTrue(access['user_id'] == str(self.user.id))

        access_token_duration = access['exp'] - access['iat']
        self.assertGreaterEqual(access_token_duration,
                                timedelta(minutes=5).seconds)

    def test_refresh_token_validity(self):
        refresh = self.refresh_decoded
        refresh_token_duration = refresh['exp'] - refresh['iat']
        self.assertGreaterEqual(refresh_token_duration,
                                timedelta(days=7).seconds)

    def test_get_tokens_for_user_with_invalid_user_returns_none(self):
        tokens = JWTUtils.get_tokens_for_user()  # Test without passing user
        self.assertIsNone(tokens)

        # Test with an invalid user
        invalid_user = User(username='invaliduser')
        tokens = JWTUtils.get_tokens_for_user(invalid_user)
        self.assertIsNone(tokens)


class LoginOTPUtilsTestCase(TestCase):

    def setUp(self) -> None:
        user_data = {
            "username": "test.user.001",
            "password": "Te$tpassw0rd",
            "email": "test.user.001@test.com"
        }
        try:
            self.user, _ = User.objects.get_or_create(**user_data)
        except Exception as ex:
            logger.exception(ex)

        _ = UserLoginOTP.objects.filter(user=self.user).delete()

    def test_generate_text_otp(self):
        otp = LoginOTPUtils.generate_text_otp()
        self.assertEqual(len(otp), LoginOTPUtils.OTP_SIZE)
        # Check if OTP contains only uppercase letters
        self.assertRegex(otp, '^[A-Z]+$')

    def test_generate_numeric_otp(self):
        otp = LoginOTPUtils.generate_numeric_otp()
        self.assertEqual(len(otp), LoginOTPUtils.OTP_SIZE)
        # Check if OTP contains only numeric digits
        self.assertRegex(otp, '^[0-9]+$')

    def test_generate_hex_otp(self):
        otp = LoginOTPUtils.generate_hex_otp()
        self.assertEqual(len(otp), LoginOTPUtils.OTP_SIZE)
        # Check if OTP is a valid hex string
        self.assertRegex(otp, '^[A-F0-9]+$')

    def test_assign_otp_to_user(self):
        otp = LoginOTPUtils.generate_numeric_otp()
        otp_instance = LoginOTPUtils.assign_otp_to_user(self.user, otp)
        self.assertIsNotNone(otp_instance)
        self.assertEqual(otp_instance.user, self.user)
        self.assertTrue(check_password(otp, otp_instance.otp))
        self.assertTrue(otp_instance.otp_expires_at > timezone.now())
        self.assertTrue(otp_instance.otp_expires_at <= timezone.now(
        ) + timedelta(minutes=LoginOTPUtils.OTP_EXPIRY_MINUTES))

        # Test invalid arguments
        invalid_user = None
        invalid_otp = "123"
        self.assertIsNone(LoginOTPUtils.assign_otp_to_user(invalid_user, otp))


class UserTokenUtilsTestCase(TestCase):

    def setUp(self) -> None:
        user_data = {
            "username": "test.user.001",
            "password": "Te$tpassw0rd",
            "email": "test.user.001@test.com"
        }
        try:
            self.user, _ = User.objects.get_or_create(**user_data)
        except Exception as ex:
            logger.exception(ex)

    def test_generate_hex_token(self):
        token = UserTokenUtils.generate_hex_token()
        self.assertEqual(len(token), UserTokenUtils.TOKEN_SIZE*2)
        # Check if token is a valid hex string
        self.assertRegex(token, '^[A-F0-9]+$')

    def test_process_user_salt(self):
        salt = UserTokenUtils.process_user_salt(self.user)
        self.assertEqual(len(salt), UserTokenUtils.SALT_01_SIZE *
                         2 + len(str(self.user.id)) + UserTokenUtils.SALT_02_SIZE*2)

    def test_split_parts(self):
        token = UserTokenUtils.create_permanent_token(self.user)
        user_part, token_part = UserTokenUtils.split_parts(token)
        self.assertIsNotNone(user_part)
        self.assertIsNotNone(token_part)
        self.assertEqual(user_part + token_part, token)

    def test_get_user_id(self):
        token = UserTokenUtils.create_permanent_token(self.user)
        user_id = UserTokenUtils.get_user_id(token=token)
        self.assertEqual(user_id, str(self.user.id))

    def setDown(self) -> None:
        self.user.delete()
