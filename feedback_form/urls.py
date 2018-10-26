from django.conf.urls import url

from . import views

app_name = 'feedback_form'
urlpatterns = [
    url(r'^$', views.feedback_form, name='home'),
]