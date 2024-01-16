from datetime import datetime, timedelta
import pytz

from django_cron import CronJobBase, Schedule

from django.conf import settings

from database.collections import DatabaseCollections
from database.methods import SynchronousMethods

from middleware_app import logger


class DeleteOldUserIPAddresses(CronJobBase):
    """
    Delete IP addresses older than 90 days.
    """
    RUN_EVERY_MINS = 120  # every 2 hours
    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'delete_old_user_ip_addresses'  # a unique code
    
    def do(self):
        """
        Delete IP addresses older than 90 days or approximately, 3 months.
        """
        NINETY_DAYS_AGO = datetime.now(pytz.timezone(settings.TIME_ZONE)) - timedelta(days=90)
        logger.info("Deleting old IP addresses.")
        try:
            SynchronousMethods.delete(
                filter_dict={
                    "timestampUtc": {
                        "$lt": NINETY_DAYS_AGO
                    }
                },
                collection=DatabaseCollections.user_ips
            )
        except Exception as ex:
            logger.warn(f"{ex}")


class DeleteOldUserMACAdresses(CronJobBase):
    """
    Delete MAC addresses older than 90 days.
    """
    RUN_EVERY_MINS = 120  # every 2 hours
    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'delete_old_user_mac_addresses'  # a unique code
    
    def do(self):
        """
        Delete MAC addresses older than 30 days.
        """
        NINETY_DAYS_AGO = datetime.now(pytz.timezone(settings.TIME_ZONE)) - timedelta(days=90)
        logger.info("Deleting old MAC addresses.")
        try:
            SynchronousMethods.delete(
                filter_dict={
                    "timestampUtc": {
                        "$lt": NINETY_DAYS_AGO
                    }
                },
                collection=DatabaseCollections.user_mac_addresses
            )
        except Exception as ex:
            logger.warn(f"{ex}")