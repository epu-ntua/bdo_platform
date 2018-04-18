from django.conf.urls import url
from . import views

app_name = 'requestservice'

urlpatterns = [

    # requests/
    url(r'^$', views.IndexList.as_view(), name='index'),

    # requests/users
    url(r'^users/$', views.ajaxcall, name='fetchd'),

    # requests/462/
    url(r'^(?P<pk>[0-9]+)/$', views.Detail.as_view(), name='detail'),

    # requests/searchres/
    url(r'^searchres/$', views.SearchView.as_view(), name='search'),

    # requests/463/discussion/
    url(r'^(?P<pk>[0-9]+)/discussion/$', views.Discussion.as_view(), name='reqdiscusion'),

    # requests/444/discussion/close
    url(r'^(?P<pk>[0-9]+)/discussion/close$', views.closeRequest, name='closereq'),

    # requests/create/
    url(r'^create/$', views.Create.as_view(), name='create'),

    # requests/345/update
    url(r'^(?P<pk>[0-9]+)/update/$', views.Update.as_view(), name='update'),

    # login/
    url(r'^login/$', views.UserLogin.as_view(), name='login'),

    # register/
    url(r'^register/$', views.UserFormView.as_view(), name='register'),

    # logout/
    url(r'^logout/$', views.UserLogout, name='user-logout'),

]
