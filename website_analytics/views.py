# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from website_analytics.models import *

def dataset_display(dataset_obj):
    try:
        dataset = DatasetPageViews.objects.get(dataset=dataset_obj)
        dataset.preview_count = dataset.preview_count + 1
        dataset.save()
        print 'Dataset display increment'
    except ObjectDoesNotExist:
        print 'Dataset display object created'
        dataset = DatasetPageViews(dataset=dataset_obj)
        dataset.save()

def unique_dataset_display(dataset_obj, user):
    try:
        dataset = DatasetUniqueViews.objects.get(dataset=dataset_obj, dataset_user=user)
        dataset.preview_count = dataset.preview_count + 1
        dataset.save()
        print 'Dataset display increment'
    except ObjectDoesNotExist:
        print 'Dataset display object created'
        dataset = DatasetUniqueViews(dataset=dataset_obj, dataset_user=user)
        dataset.save()

def dataset_exploration(dataset_obj):
    try:
        dataset = DatasetExplored.objects.get(dataset=dataset_obj)
        dataset.exploration_count = dataset.exploration_count + 1
        dataset.save()
        print 'Dataset exploration increment'
    except ObjectDoesNotExist:
        print 'Dataset exploration object created'
        dataset = DatasetExplored(dataset=dataset_obj)
        dataset.save()

def dataset_visualisation(dataset_obj):
    try:
        dataset = DatasetUseInVisualisation.objects.get(dataset=dataset_obj)
        dataset.viz_use_count = dataset.viz_use_count + 1
        dataset.save()
        print 'Dataset visualisation increment'
    except ObjectDoesNotExist:
        print 'Dataset visualisation object created'
        dataset = DatasetUseInVisualisation(dataset=dataset_obj)
        dataset.save()


def dataset_join(dataset_obj):
    try:
        dataset = DatasetCombined.objects.get(dataset=dataset_obj)
        dataset.combination_count = dataset.combination_count + 1
        dataset.save()
        print 'Dataset combination increment'
    except ObjectDoesNotExist:
        print 'Dataset combination object created'
        dataset = DatasetCombined(dataset=dataset_obj)
        dataset.save()

def dataset_service_execution(dataset_obj, service_obj):
    try:
        dataset = DatasetUseInService.objects.get(dataset=dataset_obj, service=service_obj)
        dataset.use_count = dataset.use_count + 1
        dataset.save()
        print 'Dataset in service increment'
    except ObjectDoesNotExist:
        print 'Dataset in service object created'
        dataset = DatasetUseInService(dataset=dataset_obj, service=service_obj)
        dataset.save()

def service_use(service_obj):
    try:
        service = ServiceUse.objects.get(service=service_obj)
        service.serv_use_count = service.serv_use_count + 1
        service.save()
        print 'Service use increment'
    except ObjectDoesNotExist:
        print 'Service use object created'
        service = ServiceUse(service=service_obj)
        service.save()

def unique_service_use(service_obj, user):
    try:
        service = ServiceUsers.objects.get(service=service_obj, service_user=user)
        service.serv_use_count = service.serv_use_count + 1
        service.save()
        print 'Service unique use increment'
    except ObjectDoesNotExist:
        print 'Service unique use object created'
        service = ServiceUsers(service=service_obj, service_user=user)
        service.save()

def visualisation_type_count(viz_obj):
    try:
        viz = VisualisationTypeUses.objects.get(visualisation=viz_obj)
        viz.viz_use_count = viz.viz_use_count + 1
        viz.save()
        print 'Visualisation use increment'
    except ObjectDoesNotExist:
        print 'Visualisation use object created'
        viz = VisualisationTypeUses(visualisation=viz_obj)
        viz.save()

def dashboard_display(dashboard_obj):
    try:
        dashboard = DashboardDisplays.objects.get(dashboard=dashboard_obj)
        dashboard.dash_display_count = dashboard.dash_display_count + 1
        dashboard.save()
        print 'Dashboard display increment'
    except ObjectDoesNotExist:
        print 'Dashboard display object created'
        dashboard = DashboardDisplays(dashboard=dashboard_obj)
        dashboard.save()


def unique_dashboard_display(dashboard_obj, user):
    try:
        dashboard = DashboardUniqueViews.objects.get(dashboard=dashboard_obj, dashboard_user=user)
        dashboard.dash_display_count = dashboard.dash_display_count + 1
        dashboard.save()
        print 'Dashboard display increment'
    except ObjectDoesNotExist:
        print 'Dashboard display object created'
        dashboard = DashboardUniqueViews(dashboard=dashboard_obj, dashboard_user=user)
        dashboard.save()


def hcmr_statistics(scenario, simulation_length, time_interval, ocean_circulation_model, wave_model, natura_layer, ais_layer):
    try:
        hcmr_obj = MareProtectionService(scenario=scenario, simulation_length=simulation_length, time_interval=time_interval, ocean_circulation_model=ocean_circulation_model, wave_model=wave_model, natura_layer=natura_layer, ais_layer=ais_layer)
        hcmr_obj.save()
        print 'Record added to hcmr log'
    except Exception,e:
       print 'Logging hcmr run failed'
       print str(e)


def nester_statistics(service, dataset):
    try:
        nester_obj = WaveEnergyResourceAssessment(service=service, dataset=dataset)
        nester_obj.save()
        print 'Record added to nester log'
    except Exception,e:
       print 'Logging nester run failed'
       print str(e)