from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

import bdo_main_app.views as views

urlpatterns = [
    # home & signup
    url('^$', views.home, name='home'),
    url('^search/$', views.search, name='search'),

    # datasets
    url('^datasets/(?P<slug>[\w-]+)/$', views.dataset, name='search'),
]
