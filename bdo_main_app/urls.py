from django.conf.urls import url

import bdo_main_app.views as views

urlpatterns = [
    # home & signup
    url('^$', views.home, name='home'),
    url('^search/$', views.search, name='search'),

    # datasets
    url('^datasets/(?P<slug>[\w-]+)/$', views.dataset, name='dataset-details'),

    # on demand
    url('^on-demand/$', views.on_demand_search, name='on-demand'),
    url('^on-demand/create/$', views.on_demand_create, name='on-demand-create'),
]
