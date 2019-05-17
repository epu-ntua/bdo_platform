# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
# from django.contrib.postgres.fields import JSONField
from django.db.models import *
from aggregator.models import Dataset
from service_builder.models import Service
from dashboard_builder.models import Dashboard
from visualizer.models import Visualization
from query_designer.models import AbstractQuery
from django.db import migrations
from django.apps import apps
from django.db.models import Count



class DatasetPageViews(Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='analytics_dataset_page_views_dataset')
    preview_count = IntegerField(default=1)

class DatasetUniqueViews(Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='analytics_dataset_unique_views_dataset')
    dataset_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_dataset_unique_views_user')
    preview_count = IntegerField(default=1)

class UniqueDatasetPreview(Model):
    dataset_id = IntegerField(default=1)
    count = IntegerField(default=1)

    class Meta:
        managed = False
        db_table = "unique_dataset_preview"


class DatasetUseInService(Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='analytics_dataset_use_in_service_dataset')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='analytics_dataset_use_in_service_service')
    use_count = IntegerField(default=1)



class DatasetExplored(Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='analytics_dataset_explored_dataset')
    exploration_count = IntegerField(default=1)

class DatasetUseInVisualisation(Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='analytics_dataset_use_in_visualisation_dataset')
    viz_use_count = IntegerField(default=1)

class DatasetCombined(Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='analytics_dataset_combined_dataset')
    combination_count = IntegerField(default=1)

class ServiceUse(Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='analytics_service_use_service')
    serv_use_count = IntegerField(default=1)

class ServiceUsers(Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='analytics_service_users_service')
    service_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_service_users_user')
    serv_use_count = IntegerField(default=1)

class UniqueServiceUsesView(Model):
    service_id = IntegerField(default=1)
    count = IntegerField(default=1)

    class Meta:
        managed = False
        db_table = "unique_service_uses_view"

class DashboardDisplays(Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='analytics_dashboard_displays_dashboard')
    dash_display_count = IntegerField(default=1)

class DashboardUniqueViews(Model):
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='analytics_dashboard_unique_views_dashboard')
    dashboard_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_dashboard_unique_views_user')
    dash_display_count = IntegerField(default=1)

class UniqueDashboardViewsView(Model):
    dashboard_id = IntegerField(default=1)
    count = IntegerField(default=1)

    class Meta:
        managed = False
        db_table = "unique_dashboard_views_view"


class VisualisationTypeUses(Model):
    visualisation = models.ForeignKey(Visualization, on_delete=models.CASCADE, related_name='analytics_visualisation_type_uses_visualisation')
    viz_use_count = IntegerField(default=1)

class MareProtectionService(Model):
    scenario = IntegerField(default=1)
    simulation_length = IntegerField(default=24)
    time_interval = IntegerField(default=2)
    ocean_circulation_model = CharField(max_length=100, default='Poseidon High Resolution Aegean Model')
    wave_model = CharField(max_length=100, default='Poseidon WAM Cycle 4 for the Aegean')
    natura_layer = BooleanField(default=False)
    ais_layer = BooleanField(default=False)

class WaveEnergyResourceAssessment(Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='analytics_nester_statistics_service')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='analytics_nester_statistics_dataset')



# run these queries in the database for the creation of the views
# create view unique_dashboard_views_view as
#     select min(id) as id, dashboard_id , count(*) from website_analytics_dashboarduniqueviews GROUP BY dashboard_id;
#
# create view unique_service_uses_view as
#     select min(id) as id, service_id , count(*) from website_analytics_serviceusers GROUP BY service_id;
#
# create view unique_dataset_preview as
#     select min(id) as id, dataset_id , count(*) from website_analytics_datasetuniqueviews GROUP BY dataset_id;
