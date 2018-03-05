# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models import *


class Service(Model):
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    # service creator
    user = ForeignKey(User)
    title = CharField(max_length=512)
    private = BooleanField(default=False)

    notebook_id = CharField(max_length=100)

    queries = JSONField()
    arguments = JSONField()

    output_html = TextField()
    output_css = TextField()
    output_js = TextField()
