import pickle
import pytz
import rq
from rq.job import Job
from typing import Callable

from django.conf import settings

from core.rq_constants import JobQ
from job_handler_app.models import EnqueuedJob
from job_handler_app.serializers import EnqueuedJobSerializer
from job_handler_app import logger, redis_logger


def enqueue_job(func: Callable, job_q: str = JobQ.DEFAULT_Q, is_async: bool = True, *args, **kwargs) -> Job:
    """
    Enqueue a job to Redis queue.
    """
    if job_q not in JobQ.ALL_QS:
        logger.warn(f"job_q must be one of {JobQ.ALL_QS}")
        return None
    try:
        job = rq.Queue(name=job_q, connection=settings.REDIS_CONN,
                       is_async=is_async).enqueue(func, *args, **kwargs)
        register_job_in_db(job=job)
    except Exception as ex:
        redis_logger.exception(f"Failed to enqueue job to {job_q} queue: {ex}")
        return None
    return job


def get_job(job_id: str = None, job_q: str = None) -> Job:
    """
    Get details of a job.
    """
    if job_q not in JobQ.ALL_QS:
        logger.warn(f"job_q must be one of {JobQ.ALL_QS}")
        return None
    if job_id is None or job_id == "":
        logger.warn("job_id must be provided")
        return None
    try:
        job = rq.Queue(
            name=job_q, connection=settings.REDIS_CONN).fetch_job(job_id)
    except Exception as ex:
        redis_logger.exception(f"Failed to fetch job {job_id} from {job_q} queue: {ex}")
        return None
    if job is None:
        logger.warn(f"Job {job_id} not found in {job_q} queue")
        job_db = EnqueuedJob.objects.filter(job_id=job_id).first()
        if not job_db:
            logger.warn(f"Job {job_id} not found in DB")
            return None
        return EnqueuedJobSerializer(job_db).data

    return job


def register_job_in_db(job: Job = None):
    """
    Register a job in DB.
    """
    try:
        data = {
            "job_id": f"{job.id}",
            "_func_name": f"{job.func_name}",
            "origin": f"{job.origin}",
            "enqueued_at": job.enqueued_at.replace(tzinfo=pytz.timezone(settings.TIME_ZONE)),
            "data": f"{pickle.loads(job.data)}" if job.data else None,
            "_kwargs": f"{job.kwargs}",
            "description": f"{job.description}"
        }

        deserialized = EnqueuedJobSerializer(data=data)
        if not deserialized.is_valid():
            logger.warn(f"Invalid data: {deserialized.errors}")
            return
        
        deserialized.save()
    except Exception as ex:
        logger.warn(f"Failed to register job {job.id} in DB: {ex}")

    return None


def find_prime_numbers(lower_bound: int, upper_bound: int) -> None:
    """
    Simple function to find prime numbers between a range; used to test the job queue implementation(s).
    """
    logger.info(
        f"Finding prime numbers between {lower_bound} and {upper_bound}")
    for number in range(lower_bound, upper_bound + 1):
        if number > 1:
            for i in range(2, number//2):
                if (number % i) == 0:
                    break
            else:
                redis_logger.info(f"Prime Number Found: {number}")
