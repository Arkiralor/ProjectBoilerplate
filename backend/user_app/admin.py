from django.contrib import admin

from user_app.models import User, UserProfile, UserAuthToken

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email")
    search_fields = ("id", "username", "email")
    ordering = ("-date_joined",)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "first_name", "last_name")
    search_fields = (
        "first_name",
        "last_name",
        "user__id",
        "user__username",
        "user__email"
    )
    raw_id_fields = ("user",)
    ordering = ("-created",)


@admin.register(UserAuthToken)
class UserAuthTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created", "updated")
    search_fields = (
        "token",
        "user__id",
        "user__username",
        "user__email"
    )
