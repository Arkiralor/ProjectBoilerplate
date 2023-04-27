from django.contrib import admin

from post_app.models import Tag, Post

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created', 'updated')
    search_fields = ('id', 'name')
    ordering = ('-created', '-updated')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'blurb', 'author', 'created')
    search_fields = (
        'id',
        'title',
        'blurb',
        'tags__name',
        'author__id',
        'author__username',
        'author__slug',
        'author__email'
    )
    ordering = ('-created', '-updated')