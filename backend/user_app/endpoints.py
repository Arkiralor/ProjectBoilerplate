from django.urls import path

from user_app.apis import AccessTestAPI, RegisterUserAPI, PasswordLoginAPI, UserAPI

PREFIX = "api/user/"

urlpatterns = [
    path('auth-test/', AccessTestAPI.as_view(), name='test-auth'),
    path('info/', UserAPI.as_view(), name='user-api'),
    path('signup/', RegisterUserAPI.as_view(), name='signup'),
    path('login/password/', PasswordLoginAPI.as_view(), name='password-login')
]