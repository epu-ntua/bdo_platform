from django.conf.urls import url

import bdo_main_app.views as views
import service_builder.views as sb_views

urlpatterns = [
    # home & signup
    url('^$', views.home, name='home'),
    url('^bdo/$', views.bdohome, name='bdo'),
    url('^search/$', views.search, name='search'),


    url('^analytics-environment/$', views.search, name='search'),


    # datasets
    url('^datasets/(?P<slug>[\w-]+)/$', views.dataset, name='dataset-details'),

    # on demand
    url('^on-demand/$', views.on_demand_search, name='on-demand'),
    url('^on-demand/create/$', views.on_demand_create, name='on-demand-create'),

    # service and dashboards
    url('^services/$', views.services, name='services'), #Service Marketplace
    url('^services/dashboard/(?P<pk>\d+)/$', views.view_dashboard, name='view_dashboard'),
    url('^services/service/(?P<pk>\d+)/$', sb_views.load_service, name='load_service'),


]
