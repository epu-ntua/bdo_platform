# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models



class Feedback(models.Model):
    customer_name = models.CharField(max_length=120)
    service = models.CharField(default='', max_length=120)
    details = models.TextField(default='')
    rating = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name