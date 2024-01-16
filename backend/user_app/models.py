from datetime import datetime, timedelta
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.validators import EmailValidator, RegexValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

from core.boilerplate.model_template import TemplateModel
from user_app.model_choices import UserModelChoices

from user_app import logger


class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        unique=True,
        editable=False,
        default=uuid4
    )

    username = models.CharField(max_length=16, unique=True)
    email = models.EmailField(
        validators=[
            EmailValidator(
                message="Please enter a valid email address.",
                code="invalid_email"
            )
        ],
        unique=True
    )
    password = models.CharField(max_length=1024)
    slug = models.SlugField(max_length=250, null=True, blank=True)

    unsuccessful_login_attempts = models.PositiveIntegerField(
        default=0,
        blank=True,
        null=True,
        help_text="Number of unsuccessful login attempts"
    )
    blocked_until = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Blocked until"
    )

    date_joined = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        self.email = self.email.lower()
        self.slug = slugify(self.username)

        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('-date_joined', 'id')
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('username',)),
            models.Index(fields=('email',)),
            models.Index(fields=('slug',))
        )


class UserProfile(TemplateModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(
        max_length=16,
        blank=True,
        null=True
    )
    middle_name = ArrayField(
        models.CharField(
            max_length=16,
            blank=True,
            null=True
        ),
        size=16,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        max_length=16,
        blank=True,
        null=True
    )
    regnal_number = models.PositiveIntegerField(default=1)
    gender = models.CharField(
        max_length=32, choices=UserModelChoices.USER_GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = self.first_name.title()
        if self.last_name:
            self.last_name = self.last_name.title()
        # if self.middle_name and len(self.middle_name) > 0:
        #     for name in self.middle_name:
        #         name = name.title()
        
        self.middle_name = [name.title() for name in self.middle_name if self.middle_name]

        if self.date_of_birth:
            res = timezone.now().date() - self.date_of_birth
            self.age = res.days//365.25

        super(UserProfile, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ('-created', 'id')
        indexes = (
            models.Index(fields=('user',)),
            models.Index(fields=('first_name', 'last_name')),
        )


class UserLoginOTP(TemplateModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=1024)
    otp_expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP for {self.user.email} expiring at {self.otp_expires_at}"

    def save(self, *args, **kwargs):
        if not self.otp_expires_at:
            self.otp_expires_at = timezone.now() + timedelta(minutes=5)

        super(UserLoginOTP, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'User Login OTP'
        verbose_name_plural = 'User Login OTPs'
        ordering = ('-created', 'id')
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('user',)),
            models.Index(fields=('otp',)),
            models.Index(fields=('otp_expires_at',))
        )


class UserPasswordResetToken(TemplateModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=1024)
    token_expires_at = models.DateTimeField()

    def __str__(self):
        return f"Password reset token for {self.user.email} expiring at {self.token_expires_at}"

    def save(self, *args, **kwargs):
        if not self.token_expires_at:
            self.token_expires_at = timezone.now() + timedelta(minutes=5)

        super(UserPasswordResetToken, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'User Password Reset Token'
        verbose_name_plural = 'User Password Reset Tokens'
        ordering = ('-created', 'id')
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('user',)),
            models.Index(fields=('token',)),
            models.Index(fields=('token_expires_at',))
        )


class UserToken(TemplateModel):
    """
    Permanent token for user to make app-based API calls to the backend.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=1024)
    alias = models.CharField(max_length=64, blank=False, null=False)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Token '{self.alias if self.alias else None}' for {self.user.email} expiring at {self.expires_at}"
    
    def save(self, *args, **kwargs):
        if self.alias:
            self.alias = self.alias.lower()

        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=90)

        super(UserToken, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'User Token'
        verbose_name_plural = 'User Tokens'
        unique_together = ('user', 'alias')
        ordering = ('-created', 'id')
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('user',)),
            models.Index(fields=('alias',)),
            models.Index(fields=('expires_at',))
        )


class UserTokenUsage(TemplateModel):
    token = models.ForeignKey(UserToken, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"Token '{self.token.alias}' used by {self.token.user.email} at {self.created}"
    
    def __repr__(self):
        return self.__str__()
    
    class Meta:
        verbose_name = 'User Token Usage'
        verbose_name_plural = 'User Token Usages'
        ordering = ('-created', 'id')
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('token',)),
            models.Index(fields=('created',))
        )