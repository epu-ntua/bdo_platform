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

    # query designer
    url(r'^queries/', include('query_designer.urls')),

    # analytics
    url(r'^analytics/', include('analytics.urls')),
]
