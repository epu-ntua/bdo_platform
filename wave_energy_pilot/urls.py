from django.conf.urls import url
from wave_energy_pilot import views

urlpatterns = [
    url(r'^$', views.init, name='wave_energy_init'),
    url(r'^evaluate_location/execute/$', views.single_location_evaluation_execute, name='evaluate_location_execute'),
    url(r'^evaluate_location/results/(?P<exec_instance>[0-9]+)/$', views.single_location_evaluation_results, name='evaluate_location_results'),
    url(r'^evaluate_location/status/(?P<exec_instance>[0-9]+)/$', views.single_location_evaluation_status, name='evaluate_location_status'),
    url(r'^data_visualisation/execute/$', views.data_visualization_results, name='data_visualization_results'),
]
