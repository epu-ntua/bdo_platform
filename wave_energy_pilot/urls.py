from django.conf.urls import url
from wave_energy_pilot import views

urlpatterns = [
    url(r'^$', views.init, name='wave_energy_init'),
    url(r'^evaluate_location/$', views.execute_single_location_evaluation, name='evaluate_location$'),
]
