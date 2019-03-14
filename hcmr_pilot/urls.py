from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.init, name='hcmr_init'),
    url('process', views.execute, name='process'),
    url('status/(?P<exec_instance>[0-9]+)/$', views.status, name='status'),
    url('results/(?P<exec_instance>[0-9]+)/$', views.results, name='results'),
    url('download', views.download, name='download'),
    url('form', views.index, name='index'),
]