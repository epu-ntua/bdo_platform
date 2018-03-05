from django.conf.urls import url
from service_builder import views

urlpatterns = [
    url('^create/$', views.create_new_service, name='create_new_service'),
    url('^load_query/$', views.load_query, name='load_query'),

    url('^publish/$', views.publish_new_service, name='publish_new_service'),
]
