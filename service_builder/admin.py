# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Register your models here.
from django.contrib import admin
from service_builder.models import *


class ServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Service._meta.get_fields()]


admin.site.register(Service, ServiceAdmin)
