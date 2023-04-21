from django.db import models

from core.boilerplate.model_template import TemplateModel
from user_app.models import User

class RequestLog(TemplateModel):
    method = models.TextField(blank=True, null=True)
    path = models.TextField(blank=True, null=True)
    cookie = models.TextField(blank=True, null=True)
    body = models.BinaryField(max_length=1_073_741_824, blank=True, null=True)
    body_text = models.TextField(blank=True, null=True)
    headers = models.TextField(blank=True, null=True)
    params = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Request at {self.created}"
    
    class Meta:
        verbose_name = "Incoming Request"
        verbose_name_plural = "Incoming Requests"
        ordering = ("-created",)
