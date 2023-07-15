from rq.job import Job

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from job_handler_app.serializers import RQJobSerializer
from job_handler_app.utils import enqueue_job, get_job, find_prime_numbers

from job_handler_app import logger


class TestEnqueue(APIView):
    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:
        job_id = request.query_params.get('job', None)
        job_q = request.query_params.get('jobQ', 'default')
        instance = get_job(job_id=job_id, job_q=job_q)
        if not isinstance(instance, Job):
            return Response(
                instance,
                status=status.HTTP_200_OK
            )

        return Response(
            RQJobSerializer(instance).data,
            status=status.HTTP_200_OK
        )

    def post(self, request: Request) -> Response:
        """
        Test endpoint to enqueue a job.
        """
        lower_bound = int(request.data.get('lower', 10))
        upper_bound = int(request.data.get('upper', 100))

        if lower_bound > upper_bound:
            return Response(
                {'error': 'lower_bound must be less than upper_bound'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if lower_bound < 4:
            return Response(
                {'error': 'lower_bound must be greater than 3'},
                status=status.HTTP_400_BAD_REQUEST
            )
        job = enqueue_job(
            func=find_prime_numbers,
            job_q='default',
            lower_bound=lower_bound,
            upper_bound=upper_bound
        )
        logger.info(
            f"Enqueued job {job.id} to find prime numbers between {lower_bound} and {upper_bound}")
        return Response(
            RQJobSerializer(job).data,
            status=status.HTTP_200_OK
        )