from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.init, name='hcmr_init'),
    url('scenario1/process/', views.execute, name='scenario1-process'),
    url('scenario1/status/(?P<exec_instance>[0-9]+)/$', views.status, name='scenario1-status'),
    url('scenario1/results/(?P<exec_instance>[0-9]+)/$', views.scenario1_results, name='scenario1-results'),

    url('scenario2/process/', views.execute, name='scenario2-process'),
    url('scenario2/status/(?P<exec_instance>[0-9]+)/$', views.status, name='scenario2-status'),
    url('scenario2/results/(?P<exec_instance>[0-9]+)/$', views.scenario2_results, name='scenario2-results'),

    url('scenario3/process/', views.execute, name='scenario3-process'),
    url('scenario3/status/(?P<exec_instance>[0-9]+)/$', views.status, name='scenario3-status'),
    url('scenario3/results/(?P<exec_instance>[0-9]+)/$', views.scenario3_results, name='scenario3-results'),

    url('download', views.download, name='download'),
    url('form', views.index, name='index'),
    url('create_natura_grid/', views.create_map_grid_for_natura, name='natura_grid'),

    url(r'^cancel_execution/(?P<exec_instance>[0-9]+)/$', views.cancel_execution, name='cancel_execution')
]