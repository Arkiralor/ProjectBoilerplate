# Generated by Django 4.2 on 2023-04-26 20:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('post_app', '0003_alter_post_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, to='post_app.tag'),
        ),
        migrations.AlterUniqueTogether(
            name='post',
            unique_together={('title', 'body', 'author')},
        ),
    ]
