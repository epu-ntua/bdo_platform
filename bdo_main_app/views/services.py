from datetime import timedelta

import collections
from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils.timezone import now

# from bdo_main_app.models import Service
from dashboard_builder.models import Dashboard
from service_builder.models import Service
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from access_controller.policy_enforcement_point import PEP


def services(request):
    user = request.user
    if user.is_authenticated:
        user_dashboards = Dashboard.objects.filter(user=user).order_by('id')
        user_services = Service.objects.filter(user=user, published=True).order_by('id')
    else:
        user_dashboards = []
        user_services = []
    bdo_dashboards = Dashboard.objects.filter(private=False)
    bdo_services = Service.objects.filter(published=True, private=False)

    return render(request, 'services/services/services_index.html', {
        'my_dashboards': user_dashboards,
        'bdo_dashboards': bdo_dashboards,
        'my_services': user_services,
        'bdo_services': bdo_services,
    })


def convert_unicode_json(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_unicode_json, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_unicode_json, data))
    else:
        return data


def view_dashboard(request, pk):
    user = request.user
    dashboard = Dashboard.objects.get(pk=pk)
    # check for the access
    try:
        access_decision = PEP.access_to_dashboard(request, dashboard.id)
        if access_decision is False:
            raise PermissionDenied
    except:
        return HttpResponseForbidden()
    # check if user is the owner or just has been granted access
    owner = False
    if dashboard.user_id == user.id:
        owner = True
    dashboard.viz_components = convert_unicode_json(dashboard.viz_components)
    print dashboard.viz_components
    return render(request, 'services/services/view_dashboard.html', {
        'dashboard': dashboard,
        'pk': pk,
        'is_owner': owner
    })


def view_service(request, pk):
    user = request.user
    service = Service.objects.get(pk=pk)

    # check for the access
    try:
        access_decision = PEP.access_to_service(request, service.id)
        if access_decision is False:
            raise PermissionDenied
    except:
        return HttpResponseForbidden()

    return render(request, 'service_builder/load_service.html', {
        'service_id': service.id,
        'output_html': service.output_html,
        'output_css': service.output_css,
        'output_js': service.output_js,
        'published': service.published
    })