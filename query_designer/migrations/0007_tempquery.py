# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-09 16:41
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('query_designer', '0006_auto_20180202_1527'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempQuery',
            fields=[
                ('query_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='query_designer.Query')),
                ('args', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('original', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='query_designer.Query')),
            ],
            bases=('query_designer.query',),
        ),
    ]
