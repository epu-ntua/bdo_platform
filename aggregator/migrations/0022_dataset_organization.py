# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-18 11:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aggregator', '0021_update_organizations'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='organization',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='dataset_organization', to='aggregator.Organization'),
        ),
    ]
