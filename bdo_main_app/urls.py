from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

import bdo_main_app.views as views
import analytics.views as analytic_views

urlpatterns = [
    # home & signup
    url('^$', views.home, name='home'),
    url('^search/$', views.search, name='search'),

    # datasets
    url('^datasets/(?P<slug>[\w-]+)/$', views.dataset, name='dataset-details'),

    # on demand
    url('^on-demand/$', views.on_demand_search, name='on-demand'),
    url('^on-demand/create/$', views.on_demand_create, name='on-demand-create'),

    # analytics
    # base analytics
    url('^analytics/create/$', analytic_views.pick_base_analysis, name='basic-analytics-pick-base-analysis'),
    url('^analytics/create/(?P<base_analysis_id>\d+)/config/$', analytic_views.config_base_analysis, name='basic-analytics-config'),
    url('^analytics/jobs/(?P<pk>\d+)/$', analytic_views.view_job_details, name='analytics-job-details'),
    url('^analytics/jobs/(?P<pk>\d+)/update/$', analytic_views.update_job, name='update-analytics-job'),
]
