# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from aggregator.models import *
from threading import Thread
import json
from django.http import JsonResponse

from django.contrib.auth.models import User

# Create your models here.

class Wave_energy_converters(models.Model):
   title = models.CharField(max_length=200)
   owner_id = models.ForeignKey(User, default=None)
   image_uri = models.CharField(max_length=200)
   sample_rows = JSONField()
   min_height = models.FloatField(null=True, blank=True, default=None)
   max_height = models.FloatField(null=True, blank=True, default=None)
   min_energy_period = models.FloatField(null=True, blank=True, default=None)
   max_energy_period = models.FloatField(null=True, blank=True, default=None)
   nominal_power = models.FloatField(null=True, blank=True, default=None)
   height_step = models.FloatField(null=True, blank=True, default=None)
   period_step = models.FloatField(null=True, blank=True, default=None)