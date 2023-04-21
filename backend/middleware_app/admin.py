from django.contrib import admin
from middleware_app.models import RequestLog

@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ("user", "method", "path", "created")
    raw_id_fields = ("user",)
    ordering = ("-created", "-updated")