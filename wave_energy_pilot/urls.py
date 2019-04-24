from django.conf.urls import url
from wave_energy_pilot import views

urlpatterns = [
    url(r'^$', views.init, name='wave_energy_init'),
    # SC1_TC1 - SINGLE LOCATION EVALUATION
    url(r'^evaluate_location/execute/$', views.single_location_evaluation_execute, name='evaluate_location_execute'),
    url(r'^evaluate_location/results/(?P<exec_instance>[0-9]+)/$', views.single_location_evaluation_results, name='evaluate_location_results'),
    url(r'^evaluate_location/status/(?P<exec_instance>[0-9]+)/$', views.single_location_evaluation_status, name='evaluate_location_status'),
    # SC1_TC2 - DATA VISUALISATION
    url(r'^data_visualisation/execute/$', views.data_visualization_results, name='data_visualization_results'),
    # SC1_TC3 - AREA EVALUATION
    url(r'^evaluate_area/execute/$', views.area_location_evaluation_execute, name='evaluate_area_execute'),
    url(r'^evaluate_area/results/(?P<exec_instance>[0-9]+)/$', views.area_location_evaluation_results, name='evaluate_area_results'),
    url(r'^evaluate_area/status/(?P<exec_instance>[0-9]+)/$', views.area_location_evaluation_status, name='evaluate_area_status'),
    # SC1_TC4 - WAVE FORECAST
    url(r'^wave_forecast/execute/$', views.wave_forecast_execute, name='wave_forecast_execute'),
    url(r'^wave_forecast/results/(?P<exec_instance>[0-9]+)/$', views.wave_forecast_results, name='wave_forecast_results'),
    url(r'^wave_forecast/status/(?P<exec_instance>[0-9]+)/$', views.wave_forecast_status, name='wave_forecast_status'),

    url(r'energy_conversion/$', views.energy_conversion_init, name='energy_conversion_init'),
    # SC2_TC1 - ENERGY CONVERSION SINGLE LOCATION EVALUATION
    url(r'^energy_conversion/evaluate_location/execute/$', views.wec_single_location_evaluation_execute, name='wec_single_location_evaluation_execute'),
    url(r'^energy_conversion/evaluate_location/results/(?P<exec_instance>[0-9]+)/$', views.wec_single_location_evaluation_results, name='wec_single_location_evaluation_results'),
    url(r'^energy_conversion/evaluate_location/status/(?P<exec_instance>[0-9]+)/$', views.energy_conversion_status, name='energy_conversion_status'),
    # SC2_TC2 - ENERGY CONVERSION AREA EVALUATION
    url(r'^energy_conversion/evaluate_area/execute/$', views.wec_area_evaluation_execute, name='wec_area_evaluation_execute'),
    url(r'^energy_conversion/evaluate_area/results/(?P<exec_instance>[0-9]+)/$', views.wec_area_evaluation_results, name='wec_area_evaluation_results'),
    url(r'^energy_conversion/evaluate_area/status/(?P<exec_instance>[0-9]+)/$', views.energy_conversion_status, name='energy_conversion_status'),
    # SC2_TC3 - WAVE POWER GENERATION FORECAST
    url(r'^energy_conversion/generation_forecast/execute/$', views.wec_generation_forecast_execute, name='wec_generation_forecast_execute'),
    url(r'^energy_conversion/generation_forecast/results/(?P<exec_instance>[0-9]+)/$', views.wec_generation_forecast_results, name='wec_generation_forecast_results'),
    url(r'^energy_conversion/generation_forecast/status/(?P<exec_instance>[0-9]+)/$', views.energy_conversion_status, name='energy_conversion_status'),
    # SC2_TC4 - LOAD MATCHING ANALYSIS
    url(r'^energy_conversion/load_matching/execute/$', views.wec_load_matching_execute, name='wec_load_matching_execute'),
    url(r'^energy_conversion/load_matching/results/(?P<exec_instance>[0-9]+)/$', views.wec_load_matching_results, name='wec_load_matching_results'),
    url(r'^energy_conversion/load_matching/status/(?P<exec_instance>[0-9]+)/$', views.energy_conversion_status, name='energy_conversion_status'),

    url(r'energy_conversion/new_wec/', views.wec_creation, name='wec_creation'),

    # Cancel execution
    url(r'^cancel_execution/(?P<exec_instance>[0-9]+)/$', views.cancel_execution, name='cancel_execution'),

    # get load matching file data
    url(r'^energy_conversion/get_load_matching_file_data/', views.get_load_matching_file_data, name='get_load_matching_file_data'),

]
