from django.urls import path

from admin_app.apis import RequestLogsAPI

PREFIX = "api/admin/"

urlpatterns = [
    path('logs/request/', RequestLogsAPI.as_view(), name='request-logs')
]