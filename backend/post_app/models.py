from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.template.defaultfilters import slugify

from core.boilerplate.model_template import TemplateModel
from user_app.models import User


class Tag(TemplateModel):
    """
    Tags to group similiar posts together.
    """
    name = models.CharField(max_length=64, unique=True)

    def __str__(self)->str:
        return f"#{self.name}"
    
    def __repr__(self)->str:
        return self.__str__()
    
    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(Tag, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ("-created",)
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('name',))
        )


class Post(TemplateModel):
    """
    Posts made by users.
    """
    title = models.CharField(max_length=64)
    blurb = models.CharField(max_length=128, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"{self.title} by {self.author.username if self.author else 'deleted'}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def save(self, *args, **kwargs):
        self.title = self.title.title()
        if not self.blurb:
            self.blurb = self.body[:128:1]
        self.slug = slugify(f"{self.title}-by-{self.author.username}")

        super(Post, self).save(*args, **kwargs)

    
    class Meta:
        unique_together = ("title", "body", "author")
        verbose_name = "User Post"
        verbose_name_plural = "User Posts"
        ordering = ("-created",)
        indexes = (
            models.Index(fields=('id',)),
            models.Index(fields=('title',)),
            models.Index(fields=('author',)),
            models.Index(fields=('title', 'author'))
        )
