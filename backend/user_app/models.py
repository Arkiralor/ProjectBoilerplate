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
    gender = models.CharField(max_length=32, choices=UserModelChoices.USER_GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.user.email
    
    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = self.first_name.title()
        if self.last_name:
            self.last_name = self.last_name.title()        
        if self.middle_name and len(self.middle_name) > 0:
            for name in self.middle_name:
                name = name.title()

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
