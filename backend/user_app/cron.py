from datetime import datetime, timedelta
from django_cron import CronJobBase, Schedule
from pytz import timezone

from django.conf import settings
from django.db.models import Q

from user_app.models import User

class DeleteInactiveUsers(CronJobBase):
    """
    Deletes users who joined but never activated their account after 7 days.
    """
    RUN_AT_TIMES = ['00:00', '12:00'] # Run twice a day, at midnight and noon
    schedule = Schedule(run_at_times=RUN_AT_TIMES)

    code = 'delete_inactive_users'

    def do(self):
        SEVEN_DAYS_AGO: datetime = datetime.now(timezone(settings.TIME_ZONE)) - timedelta(days=7)
        _ = User.objects.filter(
            Q(is_active=False) 
            & Q(date_joined__lte=SEVEN_DAYS_AGO)
        ).delete()


class DeleteAbandonedUsers(CronJobBase):
    """
    Delete users who have not logged into their account in over 1 year and 6 months.
    """
    RUN_AT_TIMES = ['00:00', '12:00'] # Run twice a day, at midnight and noon
    schedule = Schedule(run_at_times=RUN_AT_TIMES)

    code = 'delete_abandoned_users'

    def do(self):
        ONE_YEAR_SIX_MONTHS_AGO: datetime = datetime.now(timezone(settings.TIME_ZONE)) - timedelta(days=547)
        _ = User.objects.filter(
            Q(is_active=True) 
            & Q(last_login__lte=ONE_YEAR_SIX_MONTHS_AGO)
        ).delete()