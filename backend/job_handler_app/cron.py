from django_cron import CronJobBase, Schedule

from django.db.models import Q
from django.utils import timezone

from job_handler_app.models import EnqueuedJob
from job_handler_app.model_choices import EnquedJobChoice
from job_handler_app.utils import get_job

from job_handler_app import logger

class MonitorEnqueuedJob(CronJobBase):
    """
    Monitor enqueued jobs and update their status.
    """
    RUN_EVERY_MINS = 1 # every 1 minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'monitor_enqued_jobs'    # a unique code

    def do(self):
        """
        Check for enqueued jobs that are not finished and update their status.
        """
        jobs = EnqueuedJob.objects.filter(
            ~Q(
                Q(_status=EnquedJobChoice.finished)
                | Q(_status=EnquedJobChoice.failed)
                | Q(_status=EnquedJobChoice.completed)
            )
        )

        for job in jobs:
            current_details = get_job(job_id=job.job_id, job_q=job.origin)
            if not current_details:
                continue
            
            if job._status != current_details._status:
                job._status = current_details._status
                job.save()

                if job._status == EnquedJobChoice.failed:
                    logger.warn(f"Job {job.job_id} failed")


class DeleteOldJobRecords(CronJobBase):
    """
    Delete jobs older than ~6 months from the database.
    """
    RUN_AT_TIMES = ['00:00', '12:00', ]
    schedule = Schedule(run_at_times=RUN_AT_TIMES) # every day at midnight and noon
    code = 'delete_old_job_records'    # a unique code

    def do(self):
        six_months_ago = timezone.now() - timezone.timedelta(days=180)
        _ = EnqueuedJob.objects.filter(created__lte=six_months_ago).delete()