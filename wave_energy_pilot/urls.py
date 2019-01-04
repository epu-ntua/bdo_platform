from django.conf.urls import url
from wave_energy_pilot import views

urlpatterns = [
    url(r'^$', views.init, name='wave_energy_init'),
]
