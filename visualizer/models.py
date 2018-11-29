# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models import *


class Visualization(Model):
    title = CharField(max_length=512)
    description = TextField(blank=True, default='')  # textual description of the Visualization
    hidden = BooleanField(default=False)
    icon = ImageField(upload_to='visualizer/static/visualizer/img/',
                      default='visualizer/static/visualizer/img/default-img.jpg')
    type = CharField(max_length=512, default='')
    # info has the following structure
    """
        {
            
        }
    """
    info = JSONField(default=None, null=True, blank=True)
    view_name = CharField(max_length=100)

    @property
    def parametrize_url(self):
        return '/visualizations/create/%d/config/' % int(self.pk)

    def __unicode__(self):
        return self.title
