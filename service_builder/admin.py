# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Register your models here.
from django.contrib import admin
from service_builder.models import *


class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title','description','user','queries','arguments','created','updated']


admin.site.register(Service, ServiceAdmin)


class ServiceInstanceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServiceInstance._meta.get_fields()]


admin.site.register(ServiceInstance, ServiceInstanceAdmin)


class ServiceTemplateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServiceTemplate._meta.get_fields()]


admin.site.register(ServiceTemplate, ServiceTemplateAdmin)
