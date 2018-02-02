from django.conf.urls import url
from dashboard_builder import views

urlpatterns = [
    url('^create/$', views.build_dynamic_dashboard, name='build_dynamic_dashboard'),
    url('^get_visualization_form_fields$', views.get_visualization_form_fields, name='get_visualization_form_fields'),
]
