"""
Initialize the logger for the application.
"""
from os import path, makedirs
import logging

from django.conf import settings

logger = logging.getLogger('logger.' + __name__)
redis_formatter = logging.Formatter('[%(levelname)s|%(asctime)s.%(msecs)d|%(name)s|%(module)s|%(funcName)s:%(lineno)s]    %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
redis_handler = logging.FileHandler(filename=path.join(settings.LOG_DIR, 'redis.log'))
redis_handler.setFormatter(redis_formatter)

redis_logger = logging.getLogger('logger.redis')
redis_logger.addHandler(redis_handler)
default_app_config = 'job_handler_app.apps.JobHandlerAppConfig'