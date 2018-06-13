from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.parse_form, name='parse-form'),
]
