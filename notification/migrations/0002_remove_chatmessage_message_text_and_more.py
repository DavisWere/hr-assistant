# Generated by Django 5.2.4 on 2025-07-05 08:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatmessage',
            name='message_text',
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='sender_type',
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='timestamp',
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='conversation',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
