from django.conf.urls import url

from . import views

urlpatterns = [
    url('process', views.process, name='process'),
    url('form', views.index, name='index'),
]