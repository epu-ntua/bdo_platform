# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# Register your models here.
from django.contrib import admin
from visualizer.models import *


class VisualizationAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'hidden', 'info', 'view_name',)


admin.site.register(Visualization, VisualizationAdmin)
