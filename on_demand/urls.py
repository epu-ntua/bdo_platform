from django.conf.urls import url
import views

urlpatterns = [
    url('^$', views.OnDemandRequestListView.as_view(), name='on-demand-list'),
    url('^create/$', views.on_demand_create, name='on-demand-create'),
    url('^(?P<pk>\d+)/', views.OnDemandRequestDetailView.as_view(), name='on-demand-details'),
]
