from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

import query_designer.views as views

urlpatterns = [
    # api
    url('datasets/$', views.datasets),
    url('datasets/(?P<dataset_id>[\w-]+)/variables/$', views.dataset_variables),
    url('datasets/(?P<dataset_id>[\w-]+)/variables/(?P<variable_id>[\w-]+)/properties/$', views.dataset_variable_properties),
    url('datasets/(?P<dataset_id>[\w-]+)/variables/(?P<variable_id>[\w-]+)/count/$', views.count_variable_values),

    # execute
    url('execute/$', views.execute_query, name='execute-query'),
    url('execute/(?P<pk>\d+)/$', views.execute_query, name='execute-query'),

    # load
    url('load/(?P<pk>\d+)/$', views.load_query, name='load-query'),

    # save
    url('save/$', views.save_query, name='save-query'),
    url('save/(?P<pk>\d+)/$', views.save_query, name='save-query'),

    # get select variables
    url('get_query_variables/(?P<pk>\d+)/$', views.get_query_variables, name='get-query-variables'),

    # basic page
    url('$', views.index, name='home'),
]
