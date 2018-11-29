# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-06-21 10:21
from __future__ import unicode_literals

from django.db import connections
from django.db import migrations


def forwards(_, __):
    update_organization_for_dataset()


def update_organization_for_dataset():
    query = build_query()
    execute_query(query)


def build_query():
    return """UPDATE aggregator_dataset d 
              SET organization_id = (
                SELECT id 
                FROM aggregator_organization o 
                WHERE o.title = d.source)
              """





def execute_query(query):
    cursor = connections['default'].cursor()
    cursor.execute(query)


class Migration(migrations.Migration):
    dependencies = [
        ('aggregator', '0022_dataset_organization'),
    ]

    operations = [
        migrations.RunPython(forwards)
    ]
