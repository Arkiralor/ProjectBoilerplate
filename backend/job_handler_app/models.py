from django.db import models

from django.db import models

from core.boilerplate.model_template import TemplateModel
from job_handler_app.model_choices import EnquedJobChoice

class EnqueuedJob(TemplateModel):

    job_id = models.CharField(max_length=255, unique=True)
    _func_name = models.CharField(max_length=255)
    _status = models.CharField(max_length=255, choices=EnquedJobChoice.STATUS_CHOICES, default=EnquedJobChoice.queued)
    origin = models.CharField(max_length=255, help_text='The queue of the job')
    enqueued_at = models.DateTimeField()
    data = models.JSONField(default=dict, blank=True, null=True)
    _kwargs = models.JSONField(default=dict, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.job_id} - {self._func_name} - {self._status} - {self.origin} - {self.enqueued_at}'
    
    def __repr__(self):
        return self.__str__()
    
    class Meta:
        verbose_name = 'Enqueued Job'
        verbose_name_plural = 'Enqueued Jobs'
        ordering = ('-created',)
        indexes = (
            models.Index(fields=['job_id', 'origin']),
        )