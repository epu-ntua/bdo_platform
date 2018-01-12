# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from aggregator.models import *


class DimensionAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'description', 'stored_at')
    list_filter = ('stored_at', )


admin.site.register(Dataset, DimensionAdmin)


class DimensionAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'unit', 'min', 'max', 'step', 'variable', 'dataset', )

    def dataset(self, obj):
        return obj.variable.dataset


admin.site.register(Dimension, DimensionAdmin)


class VariableAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'unit', 'dataset', )


admin.site.register(Variable, VariableAdmin)
