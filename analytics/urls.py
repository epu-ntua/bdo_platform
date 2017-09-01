from django.conf.urls import url
from analytics import views

urlpatterns = [
    # base analytics
    url('^create/$', views.pick_base_analysis, name='basic-analytics-pick-base-analysis'),
    url('^create/(?P<base_analysis_id>\d+)/config/$', views.config_base_analysis, name='basic-analytics-config'),
    url('^jobs/(?P<pk>\d+)/$', views.view_job_details, name='analytics-job-details'),
    url('^jobs/(?P<pk>\d+)/update/$', views.update_job, name='update-analytics-job'),
]
