from django.conf.urls import url
import views

urlpatterns = [
    url('^edit/$', views.update_profile, name='update-profile'),
    url('^(?P<username>[\w.@+-]+)/$', views.show_profile, name='show-profile'),
]
