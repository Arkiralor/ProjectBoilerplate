import re
from datetime import datetime
from email.mime.base import MIMEBase
from typing import Dict, List, Sequence, Optional

import boto3

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from core.boilerplate.response_template import Resp
from core.rq_constants import JobQ
from core.settings import (APP_NAME, AWS_ACCESS_KEY_ID, AWS_REGION_NAME,
                           AWS_SECRET_ACCESS_KEY, CONTACT_EMAIL, DOMAIN_URL,
                           ENV_TYPE, OWNER_EMAIL, SNS_SENDER_ID)
from job_handler_app.utils import enqueue_job
from pytz import timezone
from rest_framework import status
from user_app.constants import FormatRegex
from user_app.models import User

from communications_app import logger


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

        if (not subject) or (not message) or subject == cls.BLANK or message == cls.BLANK:
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
            f"Your account on {cls.app_name} was logged into at {user.last_login}.\n"\
            f"If this was you, you don't need to do anything and you can disregard this email.\n"\
            f"However, if this was not you, we suggest that you change your login credentials ASAP."
        subject = f"Login Notification for {cls.app_name}"
        users = [
            user.email
        ]

        resp = cls.send_plaintext_email(
            subject=subject, message=message, recievers=users)

        return resp


class DjangoEmailUtils:
    """
    Utilities/methods to send emails via Django's built-in email system.
    """

    VALID_RESPONSE_CODES = (int(f"20{item}") for item in range(0, 10, 1))

    @classmethod
    def send_email(
        cls,
        subject: str = None,
        body: str = None,
        cc: Optional[Sequence[str]] = None,
        from_email: str = CONTACT_EMAIL,
        to: Sequence[str] = None,
        bcc: Optional[Sequence[str]] = None,
        attachements: Optional[Sequence[MIMEBase]] = None,
        headers: Optional[Dict[str, str]] = None,
        *args,
        **kwargs
    ):
        try:
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=from_email,
                to=to,
                cc=cc,
                bcc=bcc,
                attachments=attachements,
                headers=headers
            )
        except Exception as ex:
            logger.error(f"Error while creating email: {ex}")
            return False

        try:
            job = enqueue_job(func=email.send, job_q=JobQ.EMAIL_Q)
            if not job or not job.id:
                logger.error(f"Error while sending email: {email}")
                return False
            return True
        except Exception as ex:
            logger.error(f"Error while sending email: {ex}")
            return False

    @classmethod
    def send_otp_email(cls, user: User, otp: str):
        """
        Send an email with the OTP to the user
        args:
            user: User model instance
            otp: Plaintext OTP
        """
        resp = Resp()
        recipient_list = [user.email]

        subject = f"OTP for {user.username}'s Login"
        context = {
            "user": user.username,
            "otp": otp,
            "site": settings.APP_NAME,
            "year": datetime.now(timezone(settings.TIME_ZONE)).year
        }
        body = render_to_string(
            template_name='email/otp_login.txt', context=context)

        check = cls.send_email(
            subject=subject,
            body=body,
            to=recipient_list
        )

        if not check:
            resp.error = "Email Error"
            resp.message = "Error while sending OTP email."
            resp.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            logger.warn(resp.message)
            return resp

        resp.message = f"OTP email sent successfully to {user.email}."
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp
