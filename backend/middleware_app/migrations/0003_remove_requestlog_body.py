# Generated by Django 4.2 on 2023-04-20 23:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('middleware_app', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requestlog',
            name='body',
        ),
    ]
