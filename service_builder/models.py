# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models import *
from datetime import datetime

ACCESS_REQUEST_STATUS_CHOICES = (('open', 'open'),
                                 ('accepted', 'accepted'),
                                 ('rejected', 'rejected'))


class Service(Model):
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    # service creator
    user = ForeignKey(User, related_name="service_owner")
    title = CharField(max_length=512)
    private = BooleanField(default=False)
    published = BooleanField(default=False)

    notebook_id = CharField(max_length=100)
    arguments_paragraph_id = CharField(max_length=100, null=True)

    queries = JSONField(default={}, null=True, blank=True)
    arguments = JSONField(default={}, null=True)

    output_html = TextField(null=True)
    output_css = TextField(null=True)
    output_js = TextField(null=True)

    through_livy = BooleanField(default=False)

    description = CharField(blank=True,max_length=512,null=True,default=None)
    price = CharField(max_length=50,default='free')
    imageurl = URLField(blank=True,null=True, default=None)

    access_list = ManyToManyField(User, through='ServiceAccess')

    def __unicode__(self):
        return str(self.id)


class ServiceAccess(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    service = ForeignKey(Service, on_delete=CASCADE)
    start = DateField()
    end = DateField()
    valid = BooleanField()


class ServiceTemplate(Model):
    html = TextField()
    css = TextField()
    js = TextField()


class ServiceInstance(Model):
    service = ForeignKey(Service)
    user = ForeignKey(User)
    time = DateTimeField()
    arguments = JSONField(null=True, blank=True, default=None)
    notebook_id = CharField(null=True, max_length=100)
    livy_session = IntegerField(null=True)
    status = CharField(null=True, default='', max_length=100)
    output_page = CharField(null=True, default='', max_length=100)
    dataframe_visualizations = JSONField(null=True, blank=True, default=None)
    result = JSONField(null=True, blank=True, default=None)


class ServiceAccessRequest(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    resource = ForeignKey(Service, on_delete=CASCADE, related_name='resource')
    status = CharField(max_length=20, choices=ACCESS_REQUEST_STATUS_CHOICES, default='open')
    creation_date = DateTimeField(default=datetime.now())
    response_date = DateTimeField(null=True)

    @property
    def type(self):
        return 'service'
