# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-01 15:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aggregator', '0030_merge_20181201_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='order',
            field=models.IntegerField(default=999),
        ),
    ]
