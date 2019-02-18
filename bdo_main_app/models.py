# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta
from random import randint

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models import *
from django.utils.timezone import now

from bdo_main_app.lists import *


class Service(Model):
    """
    Service in BDO is an abstract term referring to the following:
        1) Dataset
        2) Query
        3) Analysis
        4) Report
    """
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    # service provider
    user = ForeignKey(User, related_name='services')
    title = CharField(max_length=512)
    moto = CharField(max_length=1024, blank=True, null=True, default=None)  # a punchline for promotional purposes
    description = TextField(blank=True, default='')  # textual description of the service
    tags_raw = TextField(blank=True, default='')  # comma-separated list of tags
    service_type = CharField(max_length=32, choices=SERVICE_TYPES_CHOICES)
    hidden = BooleanField(default=False)

    # info has the following structure
    """
        {
            object_id: <Related object ID e.g dataset ID, query ID etc.>
            coverage (optional): {location (optional), period (optional)}
            ...

            (for Analysis)
            extendable: Boolean
            arguments: List of arguments
            ...
        }
    """
    info = JSONField(default=dict())
    job_name = CharField(max_length=100)

    @property
    def tags(self):
        return self.tags_raw.split(',')

    @property
    def stats(self):
        return {'increase': 0, 'period': 'week'}

    @property
    def provider(self):
        if self.user is None:
            return 'BigDataOcean'

        return self.user.username

    @property
    def parametrize_url(self):
        if self.service_type == 'analysis':
            return '/analytics/create/%d/config/' % int(self.pk)

    @property
    def service_type_info(self):
        return [si for si in SERVICE_TYPES if si['id'] == self.service_type][0]

    def __unicode__(self):
        return self.title


class Notification(Model):
    text = TextField()
    seen = BooleanField(default=False)
    for_user = ForeignKey(User)
