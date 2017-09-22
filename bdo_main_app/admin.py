# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from django.contrib import admin
from bdo_main_app.models import *


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('created', 'updated', 'title', 'moto', 'description', 'tags_raw',
                    'service_type', 'hidden', 'info', 'job_name',)


admin.site.register(Service, ServiceAdmin)
