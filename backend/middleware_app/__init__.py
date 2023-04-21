"""
Initialize the logger for the package.
"""
import logging

default_app_config = 'middleware_app.apps.MiddlewareAppConfig'
logger = logging.getLogger('logger.' + __name__)