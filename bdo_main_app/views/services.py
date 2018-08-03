from datetime import timedelta

import collections
from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils.timezone import now

# from bdo_main_app.models import Service
from dashboard_builder.models import Dashboard
from service_builder.models import Service

from django.http import HttpResponseForbidden

def services(request):
    available_dashboards = Dashboard.objects.none()
    available_services = Service.objects.none()
    user = request.user
    if user.is_authenticated:
        username = request.user.username
        user = User.objects.get(username=username)
        available_dashboards = user.dashboard_set.all().order_by('id')
        available_services = user.service_set.all().order_by('id')

        user_dashboards = Dashboard.objects.filter(user=user,private=True).order_by('id')
        user_services = Service.objects.filter(service_user=user, published=True).order_by('id')
    else:
        user_dashboards = Dashboard.objects.none()
        user_services = Service.objects.none()

    bdo_dashboards = Dashboard.objects.filter(private=False)
    bdo_services = Service.objects.filter(published=True, private=False)
    print ('available dashboards '+str(available_dashboards))
    print ('user dashboards ' + str(user_dashboards))
    print('bdo_dashboards '+str(bdo_dashboards))
    user_dashboards =user_dashboards | available_dashboards
    user_services = user_services | available_services


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

    if user.is_authenticated:
        dashboard = Dashboard.objects.get(pk=pk)
        dashboard.viz_components = convert_unicode_json(dashboard.viz_components)
        flag = False
        if dashboard.private == False:
            flag = True
        else:
            if dashboard.user == user.username:
                flag = True
            dashboard_users = dashboard.dashboard_user.all()
            print dashboard_users
            for el in dashboard_users:
                if user.id == el.id:

                   flag = True

        if flag == True:
            print dashboard.viz_components
            return render(request, 'services/services/view_dashboard.html', {
                'dashboard': dashboard,
                'pk': pk,
            })
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()



def view_service(request, pk):
    user = request.user
    if user.is_authenticated:
        service = Service.objects.get(pk=pk)
        flag = False
        if service.private == False:
            flag = True
        else:
            if service.user == user.username:
                flag = True
            service_users = service.service_user.all()
            print service_users
            for el in service_users:
                if user.id == el.id:
                    flag = True

        if flag == True:
            return render(request, 'service_builder/load_service.html', {
                'service_id': service.id,
                'output_html': service.output_html,
                'output_css': service.output_css,
                'output_js': service.output_js,
                'published': service.published
            })
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()
