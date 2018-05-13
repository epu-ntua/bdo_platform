from datetime import timedelta

from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils.timezone import now

# from bdo_main_app.models import Service
from dashboard_builder.models import Dashboard
from service_builder.models import Service


def services(request):
    user = request.user
    if user.is_authenticated:
        user_dashboards = Dashboard.objects.filter(user=user).order_by('id')
        user_services = Service.objects.filter(user=user, published=True).order_by('id')
    else:
        user_dashboards = []
        user_services = []
    bdo_dashboards = Dashboard.objects.all()
    bdo_services = Service.objects.filter(published=True)

    return render(request, 'services/services/services_index.html', {
        'my_dashboards': user_dashboards,
        'bdo_dashboards': bdo_dashboards,
        'my_services': user_services,
        'bdo_services': bdo_services,
    })


def view_dashboard(request, pk):
    user = request.user
    dashboard = Dashboard.objects.get(pk=pk)
    return render(request, 'services/services/view_dashboard.html', {
        'dashboard': dashboard,
    })


def view_service(request, pk):
    user = request.user
    service = Service.objects.get(pk=pk)
    return render(request, 'service_builder/load_service.html', {
        'service_id': service.id,
        'output_html': service.output_html,
        'output_css': service.output_css,
        'output_js': service.output_js,
        'published': service.published
    })