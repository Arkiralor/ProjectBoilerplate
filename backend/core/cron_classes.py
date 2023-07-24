JOB_HANDLER_APP_CRON = [
    'job_handler_app.cron.MonitorEnqueuedJob',
    'job_handler_app.cron.DeleteOldJobRecords',
]
MIDDLEWARE_APP_CRON = [
    'middleware_app.cron.DeleteOldUserIPAddresses',
    'middleware_app.cron.DeleteOldUserMACAdresses',
]
USER_APP_CRON = [
    'user_app.cron.DeleteInactiveUsers',
    'user_app.cron.DeleteAbandonedUsers',
    'user_app.cron.DeleteExpiredLoginOTPs',
    'user_app.cron.DeleteExpiredUserLoginTokens'
]