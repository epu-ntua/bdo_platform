from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

import bdo_main_app.views as views

urlpatterns = [
    # home & signup
    url('^$', views.home, name='home'),

    # execute queries
    url('^execute-query/$', views.execute_query, name='execute-query')
]