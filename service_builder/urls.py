from django.conf.urls import url
from service_builder import views

urlpatterns = [
    url('^$', views.index_temp, name='index_temp'),

]
