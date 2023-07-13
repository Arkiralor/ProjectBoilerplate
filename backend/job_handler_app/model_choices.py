class EnquedJobChoice:

    queued = 'queued'
    running = 'running'
    failed = 'failed'
    completed = 'completed'
    started = 'started'
    finished = 'finished'

    STATUS_CHOICES = (
        (queued, queued),
        (running, running),
        (failed, failed),
        (completed, completed),
        (started, started),
        (finished, finished),
    )