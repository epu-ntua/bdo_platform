from django.conf.urls import url
from service_builder import views

urlpatterns = [
    url('^create/$', views.create_new_service, name='create_new_service'),
    url('^run_initial_zep_paragraph/$', views.run_initial_zep_paragraph, name='run_initial_zep_paragraph'),

    url('^load_query/$', views.load_query, name='load_query'),

    url('^publish/$', views.publish_new_service, name='publish_new_service'),

    url('service/(?P<pk>\d+)/$', views.load_service, name='load_service'),
    url('service/(?P<pk>\d+)/preview/$', views.load_service_preview, name='load_service_preview'),
    url('service/(?P<service_id>\d+)/execute/$', views.submit_service_args, name='submit_service_args'),

    url('load_service_args_form_fields/$', views.load_service_args_form_fields, name='load_service_args_form_fields'),
    url('submit_service_args/$', views.submit_service_args, name='submit_service_args'),
    url('update_service_queries/$', views.update_service_queries, name='update_service_queries'),
    url('update_service_arguments/$', views.update_service_arguments, name='update_service_arguments'),
    url('update_service_output/$', views.update_service_output, name='update_service_output'),

    url('load_template/$', views.load_template, name='load_template'),
    url('load_results_to_template/$', views.load_results_to_template, name='load_results_to_template'),

    #requests/api/createInputFileForHCMRSpillSimulator/
    url('api/createInputFileForHCMRSpillSimulator/$', views.APIcreateInputFileForHCMRSpillSimulator, name='createInputFileForHCMRSpillSimulator'),
    # requests/api/checkIfOutputExistsforHCMRSpillSimulator/
    url('api/checkIfOutputExistsforHCMRSpillSimulator/$', views.APIcheckIfOutputExistsforHCMRSpillSimulator,
        name='checkIfOutputExistsforHCMRSpillSimulator'),
]
