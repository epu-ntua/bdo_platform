# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from website_analytics.models import *


class DatasetPageViewsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DatasetPageViews._meta.get_fields()]


admin.site.register(DatasetPageViews, DatasetPageViewsAdmin)


class DatasetUniqueViewsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DatasetUniqueViews._meta.get_fields()]


admin.site.register(DatasetUniqueViews, DatasetUniqueViewsAdmin)


class DatasetExploredAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DatasetExplored._meta.get_fields()]


admin.site.register(DatasetExplored, DatasetExploredAdmin)


class DatasetUseInVisualisationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DatasetUseInVisualisation._meta.get_fields()]


admin.site.register(DatasetUseInVisualisation, DatasetUseInVisualisationAdmin)

class DatasetCombinedAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DatasetCombined._meta.get_fields()]


admin.site.register(DatasetCombined, DatasetCombinedAdmin)

class DatasetUseInServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DatasetUseInService._meta.get_fields()]


admin.site.register(DatasetUseInService, DatasetUseInServiceAdmin)


class ServiceUseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServiceUse._meta.get_fields()]


admin.site.register(ServiceUse, ServiceUseAdmin)


class ServiceUsersAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ServiceUsers._meta.get_fields()]


admin.site.register(ServiceUsers, ServiceUsersAdmin)


class VisualisationTypeUsesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in VisualisationTypeUses._meta.get_fields()]


admin.site.register(VisualisationTypeUses, VisualisationTypeUsesAdmin)


class DashboardDisplaysAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DashboardDisplays._meta.get_fields()]


admin.site.register(DashboardDisplays, DashboardDisplaysAdmin)


class DashboardUniqueViewsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DashboardUniqueViews._meta.get_fields()]


admin.site.register(DashboardUniqueViews, DashboardUniqueViewsAdmin)


class MareProtectionServiceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MareProtectionService._meta.get_fields()]


admin.site.register(MareProtectionService, MareProtectionServiceAdmin)

class WaveEnergyResourceAssessmentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in WaveEnergyResourceAssessment._meta.get_fields()]


admin.site.register(WaveEnergyResourceAssessment, WaveEnergyResourceAssessmentAdmin)


