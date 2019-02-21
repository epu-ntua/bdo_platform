# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.exceptions import PermissionDenied, ValidationError

from aggregator.models import Dataset, DatasetAccess
from dashboard_builder.models import Dashboard, DashboardAccess, DashboardAccessRequest
import datetime
import traceback
from django.http import HttpResponse, JsonResponse

from service_builder.models import Service, ServiceAccess


def requests(request):
    my_requests_dashboard_view = DashboardAccessRequest.objects.filter(user=request.user)
    my_resources_requests_dashboard = DashboardAccessRequest.objects.select_related('resource').filter(user=request.user)

    my_requests = my_requests_dashboard_view
    my_requests = my_requests.order_by('-creation_date')
    my_resources_requests = my_resources_requests_dashboard
    my_resources_requests = my_resources_requests.order_by('-creation_date')

    return render(request, 'access_controller/requests_page.html', {
        'my_requests': my_requests,
        'my_resources_requests': my_resources_requests
    })


def request_access_to_resource(request, type):
    return 1


def share_access_to_resource(request, type):
    if request.method == "POST" and request.user.is_authenticated():
        try:
            if 'request_id' in request.POST.keys():
                request_id = int(request.POST.get('request_id'))
                try:
                    if type == "dashboard":
                        access_request = DashboardAccessRequest.objects.get(pk=request_id)
                    elif type == "service":
                        access_request = DashboardAccessRequest.objects.get(pk=request_id)
                    elif type == "dataset":
                        access_request = DashboardAccessRequest.objects.get(pk=request_id)
                    else:
                        raise Exception
                    resource = access_request.resource
                    user = access_request.user
                except:
                    response = JsonResponse({"error": "Resource not found."})
                    response.status_code = 404
                    return response
            else:
                resource_id = int(request.POST.get('resource_id', '0'))
                print 'resource id'
                print resource_id
                try:
                    if type == "dashboard":
                        resource = Dashboard.objects.get(pk=resource_id)
                    elif type == "service":
                        resource = Service.objects.get(pk=resource_id)
                    elif type == "dataset":
                        resource = Dataset.objects.get(pk=resource_id)
                    else:
                        raise Exception
                except:
                    response = JsonResponse({"error": "Resource not found."})
                    response.status_code = 404
                    return response

                username_or_email = str(request.POST.get('username_or_email', ''))
                try:
                    user = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
                except:
                    response = JsonResponse({"error": "User not found."})
                    response.status_code = 404
                    return response

            can_edit = str(request.POST.get('can_edit', '')) == 'true'

            if type == "dashboard":
                if len(DashboardAccess.objects.filter(dashboard=resource, user=user)) > 0:
                    ra = DashboardAccess.objects.filter(dashboard=resource, user=user).first()
                else:
                    ra = DashboardAccess(dashboard=resource)
                ra.can_edit = can_edit
            elif type == "service":
                if len(ServiceAccess.objects.filter(service=resource, user=user)) > 0:
                    ra = ServiceAccess.objects.filter(service=resource, user=user).first()
                else:
                    ra = ServiceAccess(service=resource)
            elif type == "dataset":
                if len(DatasetAccess.objects.filter(dataset=resource, user=user)) > 0:
                    ra = DatasetAccess.objects.filter(dataset=resource, user=user).first()
                else:
                    ra = DatasetAccess(dataset=resource)
            else:
                raise Exception
            ra.start = datetime.datetime.now()
            ra.end = datetime.datetime.now() + datetime.timedelta(days=365)
            ra.valid = True
            ra.save()

            if 'request_id' in request.POST.keys():
                access_request.status = 'accepted'
                access_request.response_date = datetime.datetime.now()
                access_request.save()
            return HttpResponse('')
        except:
            traceback.print_exc()
            response = JsonResponse({"error": "Resource sharing failed."})
            response.status_code = 500  # To announce that the user isn't allowed to publish
            return response
    else:
        response = JsonResponse({"error": "Permission Denied"})
        response.status_code = 403  # To announce that the user isn't allowed to publish
        return response


def reject_access_to_resource(request, type):
    if request.method == "POST" and request.user.is_authenticated():
        try:
            if 'request_id' in request.POST.keys():
                request_id = int(request.POST.get('request_id'))
                try:
                    if type == "dashboard":
                        access_request = DashboardAccessRequest.objects.get(pk=request_id)
                    elif type == "service":
                        access_request = DashboardAccessRequest.objects.get(pk=request_id)
                    elif type == "dataset":
                        access_request = DashboardAccessRequest.objects.get(pk=request_id)
                    else:
                        raise Exception
                    resource = access_request.resource
                    user = access_request.user
                except:
                    response = JsonResponse({"error": "Resource not found."})
                    response.status_code = 404
                    return response

                access_request.status = 'rejected'
                access_request.response_date = datetime.datetime.now()
                access_request.save()
            return HttpResponse('')
        except:
            traceback.print_exc()
            response = JsonResponse({"error": "Request rejecting failed."})
            response.status_code = 500  # To announce that the user isn't allowed to publish
            return response
    else:
        response = JsonResponse({"error": "Permission Denied"})
        response.status_code = 403  # To announce that the user isn't allowed to publish
        return response

