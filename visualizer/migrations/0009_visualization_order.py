# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-01 15:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visualizer', '0008_visualization_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='visualization',
            name='order',
            field=models.IntegerField(default=999),
        ),
    ]
