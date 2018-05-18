from django.conf.urls import url
import views

urlpatterns = [
    url('^$', views.OnDemandRequestListView.as_view(), name='on-demand-list'),
    url('^create/$', views.on_demand_create, name='on-demand-create'),
    url('^(?P<pk>\d+)/accept/(?P<reply_id>\d+)/$', views.on_accept_reply, name='on-demand-accept-reply'),
    url('^(?P<pk>\d+)/upvote/$', views.on_upvote, name='on-demand-upvote'),
    url('^(?P<pk>\d+)/edit/$', views.on_demand_update, name='on-demand-update'),
    url('^(?P<pk>\d+)/reply/$', views.send_reply, name='on-demand-reply'),
    url('^(?P<pk>\d+)/', views.OnDemandRequestDetailView.as_view(), name='on-demand-details'),
]
