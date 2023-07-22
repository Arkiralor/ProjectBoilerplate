from django.urls import path

from user_app.apis import AccessTestAPI, RegisterUserAPI, PasswordLoginAPI, OTPLoginInitAPI, OTPLoginConfirmAPI, UserAPI, WhiteListIpAddressAPI, \
    UserTokenAPI

PREFIX = "api/user/"

urlpatterns = [
    path('auth-test/', AccessTestAPI.as_view(), name='test-auth'),
    path('info/', UserAPI.as_view(), name='user-api'),
    path('login/password/', PasswordLoginAPI.as_view(), name='password-login'),
    path('login/otp/init/', OTPLoginInitAPI.as_view(), name='otp-login-init'),
    path('login/otp/confirm/', OTPLoginConfirmAPI.as_view(), name='otp-login-confirm'),
    path('signup/', RegisterUserAPI.as_view(), name='signup'),
    path('token/', UserTokenAPI.as_view(), name='user-token'),
    path('whitelist-ip/', WhiteListIpAddressAPI.as_view(), name='ip-whitelist-user')
]