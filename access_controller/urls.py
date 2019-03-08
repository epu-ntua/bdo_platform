from django.conf.urls import url

from . import views

app_name = 'access_controler'
urlpatterns = [
    url(r'^request_access_to_resource/(?P<type>[\w.@+-]+)/$', views.request_access_to_resource, name='request_access_to_resource'),
    url(r'^share_access_to_resource/(?P<type>[\w.@+-]+)/$', views.share_access_to_resource, name='share_access_to_resource'),
    url(r'^reject_access_to_resource/(?P<type>[\w.@+-]+)/$', views.reject_access_to_resource, name='reject_access_to_resource'),
    url(r'^requests/$', views.requests, name='requests'),
]
