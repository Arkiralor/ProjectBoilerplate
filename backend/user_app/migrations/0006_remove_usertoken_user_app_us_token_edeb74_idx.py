# Generated by Django 4.2 on 2023-07-26 00:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0005_usertokenusage_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='usertoken',
            name='user_app_us_token_edeb74_idx',
        ),
    ]