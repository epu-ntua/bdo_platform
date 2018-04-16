# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import date
from django.contrib.auth.models import User

# Create your models here.

class UserRequests(models.Model):

    SERVICE_TYPE = (
        ('CD', 'Custom Data'),
        ('RP', 'Report'),
    )
    CATEGORY_TYPE = (
        ('C1', 'Category 1'),
        ('C2', 'Category 2'),
        ('C3', 'Category 3'),
    )
    PROVIDERS = (
        ('NT', 'NTUA'),
        ('EX', 'EXHILE'),
        ('AL', 'Every BDO Provider'),
    )
    user = models.CharField(max_length=20)
    title = models.CharField(max_length=50)
    keywords = models.TextField(max_length=500)
    service_description = models.TextField(max_length=500)
    service_type = models.CharField(max_length=2, choices=SERVICE_TYPE, default='CD')
    deadline = models.DateField(default=date.today())
    budget = models.IntegerField()
    file = models.FileField(upload_to='images/')
    category_type = models.CharField(max_length=2, choices=CATEGORY_TYPE, default='C1')
    provider = models.CharField(max_length=2, choices=PROVIDERS, default='NT')
    email_notification = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class Messages(models.Model):

    userreq = models.CharField(max_length=20)
    userpost = models.CharField(max_length=20)
    requestid = models.ForeignKey(UserRequests)
    message = models.TextField(max_length=500)
    date = models.DateTimeField(auto_now_add=True, blank=False)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)

    def __str__(self):
        return self.message + " by: " + self.userpost

class MessageNotify(models.Model):

    user = models.CharField(max_length=20)
    messageid = models.ForeignKey(Messages)
