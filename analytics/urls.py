from django.conf.urls import url
from analytics import views

urlpatterns = [
    # base analytics
    url('^create/$', views.pick_base_analysis, name='basic-analytics-pick-base-analysis'),
    url('^create/(?P<base_analysis_id>\d+)/config/$', views.config_base_analysis, name='basic-analytics-config'),
    url('^jobs/(?P<pk>\d+)/$', views.view_job_details, name='analytics-job-details'),
    url('^jobs/(?P<pk>\d+)/update/$', views.update_job, name='update-analytics-job'),

    url('^service-builder/$', views.build_dynamic_service, name='build-dynamic-service'),
    url('^get-analysis-form-fields', views.get_analysis_form_fields, name='get-analysis-form-fields')
]
