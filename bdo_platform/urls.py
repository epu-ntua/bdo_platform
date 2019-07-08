"""bdo_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    # admin
    url(r'^admin/', admin.site.urls),

    # authentication
    url(r'^accounts/', include('allauth.urls')),

    # main app
    url(r'^', include('bdo_main_app.urls')),

    # profiles
    url(r'^profile/', include('bdo_profile.urls')),

    # profiles
    url(r'^access_control/', include('access_controller.urls')),

    # query designer
    url(r'^queries/', include('query_designer.urls')),

    # hcmr pilot
    url(r'^oilspill/', include('hcmr_pilot.urls')),

    # analytics
    url(r'^analytics/', include('analytics.urls')),

    # visualizations
    url(r'^visualizations/', include('visualizer.urls')),

    # dashboards
    url(r'^dashboards/', include('dashboard_builder.urls')),

    # dashboards
    url(r'^service_builder/', include('service_builder.urls')),

    # on demand
    url(r'^on-demand/', include('on_demand.urls')),

    # uploader
    url(r'^upload/', include('uploader.urls')),

    # parser
    url(r'^parse/', include('data_parser.urls')),

    # s3direct
    url(r'^s3direct/', include('s3direct.urls')),

    url(r'^feedback/', include('feedback_form.urls')),

    # wave energy pilot urls
    url(r'^wave-energy/', include('wave_energy_pilot.urls')),
    # website_analytics
    # url(r'^website_analytics/', include('website_analytics.urls')),
    url(r'^djga/', include('google_analytics.urls'))
]
