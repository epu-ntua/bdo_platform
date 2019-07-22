from django.conf.urls import url
from dashboard_builder import views

urlpatterns = [
    url('list/$', views.list_dashboards),
    url('^create/$', views.build_dynamic_dashboard, name='build_dynamic_dashboard'),
    # url('^create/(?P<toCreate>\d+)/$', views.build_dynamic_dashboard, name='build_dynamic_dashboard'),
    # save
    url('save/$', views.save_dashboard, name='save_dashboard'),
    url('save/(?P<pk>\d+)/$', views.save_dashboard, name='save_dashboard'),

    url('delete/(?P<pk>\d+)/$', views.delete_dashboard, name='delete_dashboard'),
    url('share/(?P<pk>\d+)/$', views.delete_dashboard, name='share_dashboard'),

    url('edit/(?P<pk>\d+)/$', views.edit_dashboard, name='edit_dashboard'),

    url('^get_visualization_form_fields$', views.get_visualization_form_fields, name='get_visualization_form_fields'),
    url('^get_visualization_form_fields_df$', views.get_visualization_form_fields_df, name='get_visualization_form_fields_df'),
]
