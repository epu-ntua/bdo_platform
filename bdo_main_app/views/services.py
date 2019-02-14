from datetime import timedelta
import json
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
from django.views.decorators.cache import never_cache
from django.core.exceptions import ObjectDoesNotExist


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
    pilot_services = list()
    nester_service = {'title': 'Wave energy resource assessment',
                      'imageurl': 'https://cdn.pixabay.com/photo/2018/06/13/18/20/wave-3473335__340.jpg',
                      'targeturl': '/pilot/wave-energy/',
                      'short_description': 'A quick and reliable primary energy resource assessment that will dictate the choice of a location to create wave farms.',
                      'creator': 'R&D Nester',
                      'sharing': 'Open'}
    pilot_services.append(nester_service)
    xmile_service = {'title': 'Anomaly Detection Service',
                      'imageurl': 'https://s3.amazonaws.com/engagefp7/BDO/pilot4.jpg',
                      'targeturl': '/pilot/anomaly-detection/',
                      'short_description': 'Detect suspicious anomalies about vessels.',
                      'creator': 'XMILE',
                      'sharing': 'Private'}
    pilot_services.append(xmile_service)
    hcmr_service = {'title': 'Oil Spill Simulation Service',
                      'imageurl': 'https://thumbs-prod.si-cdn.com/bAo1rCpazij8Cq9aaICgsfyo8ZM=/800x600/filters:no_upscale()/https://public-media.si-cdn.com/filer/fa/8d/fa8d22e3-9b93-426c-bb3e-a0b8c28d122f/12685861633_1708f2dbff_o1.jpg',
                      'targeturl': '/pilot/oil-spill-simulation/',
                      'short_description': 'Define the oil spill accident detected and receive a report on the highly affected areas during the specified time period.',
                      'creator': 'HCMR',
                      'sharing': 'Open'}
    pilot_services.append(hcmr_service)
    anek_service = {'title': 'Fault Detection and Predictive Maintenance',
                      'imageurl': 'https://s3.amazonaws.com/engagefp7/BDO/pilot1b.jpg',
                      # 'targeturl': '/pilot/fault-prediction-anek/',
                      'targeturl': 'http://212.101.173.52:8065',
                      'short_description': 'Design of better and more efficient risk maintenance management strategies facilitating the estimation of the failure effect probability and the estimated time-to-live of the equipment.',
                      'creator': 'ANEK',
                      'sharing': 'Private'}
    pilot_services.append(anek_service)
    fnk_service = {'title': 'Fuel Consumption Reduction Investigation',
                      'imageurl': 'https://s3.amazonaws.com/engagefp7/BDO/pilot3.jpg',
                      # 'targeturl': '/pilot/fault-prediction-fnk/',
                      'targeturl': 'http://212.101.173.52:8062',
                      'short_description': 'Investigation of the impact of the environmental conditions and the operational decisions taken on the vessel\'s fuel consumption',
                      'creator': 'FOINIKAS',
                      'sharing': 'Private'}
    pilot_services.append(fnk_service)
    return render(request, 'services/services/services_index.html', {
        'my_dashboards': user_dashboards,
        'bdo_dashboards': bdo_dashboards,
        'my_services': user_services,
        'bdo_services': bdo_services,
        'pilot_services': pilot_services
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

@never_cache
def view_dashboard(request, pk):
    user = request.user
    try:
        dashboard = Dashboard.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return render(request, 'error_page.html',
                      {'message': 'You cannot view this Dashboard!\nThe Dashboard does not exist or has already been deleted!'})
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
        'dashboard_json': json.dumps(dashboard.viz_components),
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


def load_nester_service(request):
    return render(request, 'services/services/load_nester_service.html', {})


def load_xmile_service(request):
    return render(request, 'services/services/load_xmile_service.html', {})


def load_hcmr_service(request):
    return render(request, 'services/services/load_hcmr_service.html', {})


def load_anek_service(request):
    return render(request, 'services/services/load_anek_service.html', {})


def load_fnk_service(request):
    return render(request, 'services/services/load_fnk_service.html', {})
