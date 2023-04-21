import boto3
from communications_app import logger
from core.boilerplate.response_template import Resp
from core.settings import (APP_NAME, AWS_ACCESS_KEY_ID, AWS_REGION_NAME,
                           AWS_SECRET_ACCESS_KEY, DOMAIN_URL, ENV_TYPE,
                           SNS_SENDER_ID)
from django.utils import timezone
from rest_framework import status
from user_app.models import User


class SMSUtils:
    """
    Class to hold all functionality regarding classic SMS comminique.
    Currently we are using AWS' `Simple Notification Service` as the backend.
    """
    aws_key = AWS_ACCESS_KEY_ID
    aws_secret = AWS_SECRET_ACCESS_KEY
    aws_region = AWS_REGION_NAME
    sns_sender = SNS_SENDER_ID
    app_name = APP_NAME
    domain_url = DOMAIN_URL

    BLANK = ""

    @classmethod
    def get_client(cls):
        client = boto3.client(
            "sns",
            aws_access_key_id=cls.aws_key,
            aws_secret_access_key=cls.aws_secret,
            region_name=cls.aws_region
        )

        return client

    @classmethod
    def send_transactional_sms(cls, data: str = None, phone_no: str = None):
        """
        Unitary method to send a single TRANSACTIONAL message to a user-defined phone number.
        NOTE: Max. length of message should be below 210 characters of ASCII.
        """

        client = cls.get_client()

        if ENV_TYPE.lower() == "dev":
            return True

        try:
            req = client.publish(
                PhoneNumber=phone_no,
                Message=data,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': cls.sns_sender
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            logger.info(f"SMS Sent with Response:\t{req}")
            return True
        except Exception as ex:
            logger.warn(str(ex))
            return False

    @classmethod
    def send_promotional_message(cls, data: str = None, phone_no: str = None):
        """
        Unitary method to send a single PROMOTIONAL message to a user-defined phone number.
        NOTE: Max. length of message should be below 210 characters of ASCII.
        """

        client = cls.get_client()

        try:
            req = client.publish(
                PhoneNumber=phone_no,
                Message=data,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': cls.sns_sender
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Promotional'
                    }
                }
            )
            logger.info(f"SMS Sent with Response:\t{req}")
            return True
        except Exception as ex:
            logger.warn(str(ex))
            return False

    @classmethod
    def send_otp_message(cls, otp: str = None, phone: str = None):
        resp = Resp()

        if not otp or not phone or otp == cls.BLANK or phone == cls.BLANK:
            resp.error = "Invalid Parameters"
            resp.message = "Please provide a valid OTP and a valid Phone Number."
            resp.data = {
                "otp": otp,
                "phone": phone
            }
            resp.status_code = status.HTTP_400_BAD_REQUEST
            logger.warn(resp.text())
            return resp

        message = f"Your {cls.app_name} login OTP is {otp}."
        phone = f"+91{phone}" if not phone.startswith("+") else phone

        res = cls.send_transactional_sms(data=message, phone_no=phone)

        if not res:
            resp.error = "Message Not Sent"
            resp.message = "The login OTP message could not be sent, please contact the site administrator."
            resp.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            logger.warn(resp.text())
            return resp

        resp.message = f"OTP Message sent successfully to {phone} at {timezone.now()}."
        resp.status_code = status.HTTP_200_OK
        logger.info(resp.message)
        return resp

    @classmethod
    def send_login_notification(cls, user: User = None, phone: str = None):
        resp = Resp()

        if not user or not phone:
            resp.error = "User Not Provided"
            resp.message = "No user was provided to send the notification to."
            resp.status_code = status.HTTP_400_BAD_REQUEST

            logger.warn(resp.text())
            return resp

        phone = f"+91{phone}" if not phone.startswith("+") else phone
        time = timezone.now()
        message = f"{user.username}, you logged into {cls.app_name} utils on {time.date()} at {time.hour}:{time.minute}hrs"

        res = cls.send_transactional_sms(data=message, phone_no=phone)
        if not res:
            resp.error = "Message Not Sent"
            resp.message = "The login notification could not be sent, please contact the site administrator."
            resp.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            logger.warn(resp.text())
            return resp

        resp.message = f"Login notification sent successfully to {phone} at {time}."
        resp.data = {
            "phone": phone,
            "message": message
        }
        resp.status_code = status.HTTP_200_OK

        logger.info(resp.message)
        return resp
