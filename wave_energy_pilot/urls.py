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
    # SC2_ENERGY CONVERSION
    url(r'energy_conversion/', views.energy_conversion_init, name='energy_conversion_init'),
    url(r'energy_conversion/new_wec/', views.wec_creation, name='wec_creation'),

    # Cancel execution
    url(r'^cancel_execution/(?P<exec_instance>[0-9]+)/$', views.cancel_execution, name='cancel_execution'),

]
