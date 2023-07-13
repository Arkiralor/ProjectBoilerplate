from django.urls import path

from job_handler_app.apis import TestEnqueue

URL_PREFIX = 'api/jobs/'

urlpatterns = [
    path('test-enqueue/', TestEnqueue.as_view(), name='test-enqueue'),
]