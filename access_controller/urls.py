from django.conf.urls import url

from . import views

app_name = 'access_controler'
urlpatterns = [
    url(r'^share_access_to_dashboard/$', views.share_access_to_dashboard, name='share_access_to_dashboard'),
]
