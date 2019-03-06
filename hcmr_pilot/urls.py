from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.init, name='hcmr_init'),
    url('process', views.process, name='process'),
    url('results', views.results, name='results'),
    url('download', views.download, name='download'),
    url('form', views.index, name='index'),
]