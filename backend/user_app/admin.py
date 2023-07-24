from django.contrib import admin

from user_app.models import User, UserProfile, UserLoginOTP, UserPasswordResetToken, UserToken, UserTokenUsage

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

@admin.register(UserLoginOTP)
class UserLoginOTPAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "otp", "otp_expires_at")
    search_fields = (
        "id",
        "user__id",
        "user__username",
        "user__email"
    )
    raw_id_fields = ("user",)
    ordering = ("-created",)

@admin.register(UserPasswordResetToken)
class UserPasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "token", "token_expires_at")
    search_fields = (
        "id",
        "user__id",
        "user__username",
        "user__email"
    )
    raw_id_fields = ("user",)
    ordering = ("-created",)

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "token", "expires_at")
    search_fields = (
        "id",
        "user__id",
        "user__username",
        "user__email"
    )
    raw_id_fields = ("user",)
    ordering = ("-created",)


@admin.register(UserTokenUsage)
class UserTokenUsageAdmin(admin.ModelAdmin):
    list_display = ("id", "token", "created")
    search_fields = (
        "id",
        "token__alias",
        "token__user__id",
        "token__user__username",
        "token__user__email"
    )
    raw_id_fields = ("token",)
    ordering = ("-created",)
