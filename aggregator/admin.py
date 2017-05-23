# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from aggregator.models import *


class DefaultAdmin(admin.ModelAdmin):
    pass


admin.site.register(Dataset, DefaultAdmin)
admin.site.register(Variable, DefaultAdmin)
admin.site.register(Dimension, DefaultAdmin)
