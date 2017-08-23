# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from analytics.models import *


class JobInstanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'submitted', 'started', 'finished', 'status', )


admin.site.register(JobInstance, JobInstanceAdmin)
