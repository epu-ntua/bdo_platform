# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-06-22 09:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobinstance',
            name='finished',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='jobinstance',
            name='started',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
