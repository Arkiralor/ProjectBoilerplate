import re
from typing import List

import boto3
from communications_app import logger
from core.boilerplate.response_template import Resp
from core.settings import (APP_NAME, AWS_ACCESS_KEY_ID, AWS_REGION_NAME,
                           AWS_SECRET_ACCESS_KEY, CONTACT_EMAIL, DOMAIN_URL,
                           ENV_TYPE, OWNER_EMAIL, SNS_SENDER_ID)
from rest_framework import status
from user_app.constants import FormatRegex
from user_app.models import User


class SESEmailUtils:
    """
    Utilities/methods to send emails via AWS SES
    """

    aws_key = AWS_ACCESS_KEY_ID
    aws_secret = AWS_SECRET_ACCESS_KEY
    aws_region = AWS_REGION_NAME
    sns_sender = SNS_SENDER_ID
    app_name = APP_NAME
    domain_url = DOMAIN_URL

    BLANK = ""

    owner_email = OWNER_EMAIL
    contact_email = CONTACT_EMAIL

    CHARSET = "UTF-8"
    VALID_RESPONSE_CODES = (int(f"20{item}") for item in range(0, 10, 1))

    @classmethod
    def get_client(cls):
        client = boto3.client(
            "ses",
            aws_access_key_id=cls.aws_key,
            aws_secret_access_key=cls.aws_secret,
            region_name=cls.aws_region
        )

        return client

    @classmethod
    def verify_sender_email(cls):
        email = cls.contact_email
        client = cls.get_client()
        res = client.verify_email_identity(
            EmailAddress=email
        )

        logger.info(f"eMail verification: {res}")
        return True

    @classmethod
    def check_email_validity(cls, emails: List[str] = []) -> Resp:
        """
        Method to check if all emails provided are valid emails or not, based on format alone.
        """
        resp = Resp()

        if len(emails) == 0:
            resp.error = "No Content"
            resp.message = "No emails provided in arguments"
            resp.data = emails
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.message)
            return resp

        for item in emails:
            if not re.search(FormatRegex.EMAIL_REGEX, item):
                resp.error = "Invalid Data"
                resp.message = f"{item} is not a valid email."
                resp.data = emails
                resp.status_code = status.HTTP_400_BAD_REQUEST

                logger.warn(resp.message)
                return resp

        resp.message = "All emails valid."
        resp.data = emails
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp

    @classmethod
    def send_plaintext_email(cls, subject: str = None, message: str = None, recievers: List[str] = [], *args, **kwargs):
        """
        Basic, reusable method to send a plaintext email.
        """
        resp = Resp()

        if not subject or message or subject == cls.BLANK or message == cls.BLANK:
            resp.error = "Invalid Body"
            resp.message = "Please enter a valid message and subject"
            resp.data = {
                "subject": subject,
                "message": message
            }
            resp.status_code = status.HTTP_400_BAD_REQUEST

            return resp

        email_is_valid = cls.check_email_validity(emails=recievers)
        if email_is_valid.status_code not in cls.VALID_RESPONSE_CODES:
            return email_is_valid

        destination = {
            "ToAddresses": recievers
        }
        email_message = {
            "Body": {
                "Text": {
                    "Data": message,
                    "Charset": cls.CHARSET
                },
                "Subject": {
                    "Charset": cls.CHARSET,
                    "Data": subject
                }
            }
        }
        source = cls.CONTACT_EMAIL

        # prithoo: We don't actually want to send an email while testing in a development environment.
        if ENV_TYPE.lower() == "dev":
            resp.message = "email sending simulated as DEV environment is set."
            resp.data = {
                "email": {
                    "destination": destination,
                    "email": email_message,
                    "source": source
                }
            }
            resp.status_code = status.HTTP_200_OK
            return resp

        client = cls.get_client()
        try:
            res = client.send_email(
                Destination=destination,
                Message=email_message,
                Source=source
            )
        except Exception as ex:
            resp.error = "Client Error"
            resp.message = f"{ex}"
            resp.data = {
                "Destination": destination,
                "Message": message,
                "Source": source
            }
            resp.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

            logger.warn(resp.message)

            return resp

        resp.message = f"Message sent to {recievers}, successfully."
        resp.data = res
        resp.status_code = status.HTTP_200_OK

        return resp

    @classmethod
    def send_html_email(cls, subject: str = None, message: str = None, recievers: List[str] = [], *args, **kwargs):
        """
        Basic, reusable method to send an HTML email.

        args:
            message: str
                An HTML string.
        """
        resp = Resp()

        if not subject or message or subject == cls.BLANK or message == cls.BLANK:
            resp.error = "Invalid Body"
            resp.message = "Please enter a valid message and subject"
            resp.data = {
                "subject": subject,
                "message": message
            }
            resp.status_code = status.HTTP_400_BAD_REQUEST

            return resp

        email_is_valid = cls.check_email_validity(emails=recievers)
        if email_is_valid.status_code not in cls.VALID_RESPONSE_CODES:
            return email_is_valid

        destination = {
            "ToAddresses": recievers
        }
        email_message = {
            "Body": {
                "Text": {
                    "Html": message,
                    "Charset": cls.CHARSET
                },
                "Subject": {
                    "Charset": cls.CHARSET,
                    "Data": subject
                }
            }
        }
        source = cls.CONTACT_EMAIL

        # prithoo: We don't actually want to send an email while testing in a development environment.
        if ENV_TYPE.lower() == "dev":
            resp.message = "email sending simulated as DEV environment is set."
            resp.data = {
                "email": {
                    "destination": destination,
                    "email": email_message,
                    "source": source
                }
            }
            resp.status_code = status.HTTP_200_OK
            return resp

        client = cls.get_client()

        try:
            res = client.send_email(
                Destination=destination,
                Message=message,
                Source=source
            )
        except Exception as ex:
            resp.error = "Client Error"
            resp.message = f"{ex}"
            resp.data = {
                "Destination": destination,
                "Message": email_message,
                "Source": source
            }
            resp.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

            logger.warn(resp.message)

            return resp

        resp.message = f"Message sent to {recievers}, successfully."
        resp.data = res
        resp.status_code = status.HTTP_200_OK

        return resp

    @classmethod
    def send_plaintext_otp_email(cls, otp: str = None, user: User = None, *args, **kwargs):
        """
        Method to send the login OTP to a user's email.
        """
        message = f"Hello, {user.username},\nYour one-time-password to login to {cls.app_name} is {otp}."
        subject = f"{cls.app_name} Login OTP"
        users = [
            user.email
        ]

        resp = cls.send_plaintext_email(
            subject=subject, message=message, recievers=users)

        return resp

    @classmethod
    def send_plaintext_login_notification_email(cls, user: User = None):
        """
        Method to send a login notification to a user's email.
        """
        message = f"Hello {user.username},\n"\
            f"We thought we would let you know that your account on {cls.app_name} was logged into at {user.last_login}.\n"\
            f"If this was you, you don't need to do anything and you can disregard this email.\n"\
            f"However, if this was not you, we suggest that you change your login credentials ASAP."
        subject = f"Login Notification for {cls.app_name}"
        users = [
            user.email
        ]

        resp = cls.send_plaintext_email(
            subject=subject, message=message, recievers=users)

        return resp
