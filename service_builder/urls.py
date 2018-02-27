from django.conf.urls import url
from service_builder import views

urlpatterns = [
    url('^create/$', views.create_new_service, name='create_new_service'),

]
