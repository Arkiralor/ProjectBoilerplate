from os import path, environ, getenv
from secrets import choice
from socket import socket, AF_INET, SOCK_DGRAM, error

from utils import logger


class NetworkUtils:

    REMOTE_SERVERS = ["www.google.com", "www.facebook.com", "www.twitter.com", "8.8.8.8"]
    ENV_KEY: str = "ALLOWED_HOSTS"
    VALUE_SPERATOR: str = ", "

    # (prithoo): Get these environment variable directly from the environment as the `settings` module would not have been loaded yet.
    DEBUG = getenv("DEBUG", "False")
    ENV_TYPE = getenv("ENV_TYPE", "PROD").lower()
    SAFE_ENV: str = "dev"

    @classmethod
    def get_ip_address(cls):
        """
        Get the local IP address of the current machine.    
        """
        with socket(AF_INET, SOCK_DGRAM) as sock:
            try:
                # Connect to a remote server (doesn't matter which one)
                sock.connect((choice(cls.REMOTE_SERVERS), 80))
                
                # Retrieve the local IP address
                ip_address = sock.getsockname()[0]
                
                logger.info(f"Server IP Address:\t{ip_address}")
                return ip_address
            except error as ex:
                logger.warn(f"Socket error: {ex}")

    @classmethod
    def add_to_allowed_hosts(cls):
        """
        Edits the ALLOWED_HOSTS environment variable to add the current machine's LOCAL IP address.
        """
        if not cls.DEBUG and not cls.ENV_TYPE == cls.SAFE_ENV:
            logger.info(
                f"ENVIRONMENT TYPE: {cls.ENV_TYPE}; DEBUG: {cls.DEBUG}")
            logger.warn("This script is only for development purposes.")
            return False
        try:
            allowed_hosts = getenv(cls.ENV_KEY)
            environ[cls.ENV_KEY] = f"{allowed_hosts}{cls.VALUE_SPERATOR}{cls.get_ip_address()}"
            return True
        except Exception as ex:
            logger.error(ex)
            return False