from django.urls import path

from post_app.apis import CreatePostAPI, PostAPI


PREFIX = "api/post/"

urlpatterns = [
    path('create/', CreatePostAPI.as_view(), name='create-update-new-post'),
    path('get/', PostAPI.as_view(), name='get-user-post')
]