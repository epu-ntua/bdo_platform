# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-12 22:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_builder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboard',
            name='description',
            field=models.CharField(blank=True, default=None, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='dashboard',
            name='imageurl',
            field=models.URLField(blank=True, default=None, null=True),
        ),
    ]
