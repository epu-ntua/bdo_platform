from datetime import timedelta

from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils.timezone import now

from bdo_main_app.models import Service
from dashboard_builder.models import Dashboard


def services(request):
    user = request.user
    if user.is_authenticated:
        user_dashboards = Dashboard.objects.filter(user=user).order_by('id')
    else:
        user_dashboards = []
    bdo_dashboards = Dashboard.objects.filter(user=User.objects.get(username='BigDataOcean'))
    print user_dashboards
    print bdo_dashboards


    return render(request, 'services/services/services_index.html', {
        'my_services': user_dashboards,
        'bdo_services': bdo_dashboards,
    })


def view_service(request, pk):
    user = request.user
    dashboard = Dashboard.objects.get(pk=pk)
    print dashboard
    print dashboard.viz_components

    return render(request, 'services/services/view_service.html', {
        'dashboard': dashboard,
    })
