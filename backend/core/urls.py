from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin/', include('admin_app.endpoints')),
    path('api/user/', include('user_app.endpoints')),
]
