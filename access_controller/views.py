# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.exceptions import PermissionDenied, ValidationError

from aggregator.models import Dataset, DatasetAccess, DatasetAccessRequest
from dashboard_builder.models import Dashboard, DashboardAccess, DashboardAccessRequest
import datetime
import traceback
from django.http import HttpResponse, JsonResponse
from itertools import chain
from service_builder.models import Service, ServiceAccess, ServiceAccessRequest


def requests(request):
    my_requests_dashboard = DashboardAccessRequest.objects.filter(user=request.user)
    my_resources_requests_dashboard = DashboardAccessRequest.objects.select_related('resource').filter(user=request.user)

    my_requests_service = ServiceAccessRequest.objects.filter(user=request.user)
    my_resources_requests_service = ServiceAccessRequest.objects.select_related('resource').filter(user=request.user)

    my_requests_dataset = DatasetAccessRequest.objects.filter(user=request.user)
    my_resources_requests_dataset = DatasetAccessRequest.objects.select_related('resource').filter(user=request.user)

    my_requests = [{"id": x.id,
                    "type": x.type,
                    "resource_id": x.resource.id,
                    "resource_title": x.resource.title,
                    "user_username": x.user.username,
                    "user_email": x.user.email,
                    "status": x.status,
                    "creation_date": x.creation_date,
                    "response_date": x.response_date}
                   for x in chain(my_requests_dashboard, my_requests_service, my_requests_dataset)]

    # my_requests = my_requests.order_by('-creation_date')
    my_requests = sorted(my_requests, key=lambda k: k['creation_date'], reverse=True)
    my_resources_requests = [{"id": x.id,
                              "type": x.type,
                              "resource_id": x.resource.id,
                              "resource_title": x.resource.title,
                              "user_username": x.user.username,
                              "user_email": x.user.email,
                              "status": x.status,
                              "creation_date": x.creation_date,
                              "response_date": x.response_date}
                             for x in chain(my_resources_requests_dashboard, my_resources_requests_service, my_resources_requests_dataset)]
    # my_resources_requests = my_resources_requests.order_by('-creation_date')
    my_resources_requests = sorted(my_resources_requests, key=lambda k: k['creation_date'], reverse=True)
    return render(request, 'access_controller/requests_page.html', {
        'my_requests': my_requests,
        'my_resources_requests': my_resources_requests
    })


def request_access_to_resource(request, type):
    if request.method == "POST" and request.user.is_authenticated():
        try:
            if 'resource_id' in request.POST.keys():
                resource_id = int(request.POST.get('resource_id'))
                try:
                    if type == "dashboard":
                        resource = Dashboard.objects.get(pk=resource_id)
                        if len(DashboardAccessRequest.objects.filter(resource=resource, user=request.user, response_date=None, status='open')) > 0:
                            access_request = DashboardAccessRequest.objects.filter(resource=resource, user=request.user, response_date=None).first()
                            access_request.creation_date = datetime.datetime.now()
                        else:
                            access_request = DashboardAccessRequest(resource=resource, user=request.user)
                    elif type == "service":
                        resource = Service.objects.get(pk=resource_id)
                        if len(ServiceAccessRequest.objects.filter(resource=resource, user=request.user, response_date=None, status='open')) > 0:
                            access_request = ServiceAccessRequest.objects.filter(resource=resource, user=request.user, response_date=None).first()
                            access_request.creation_date = datetime.datetime.now()
                        else:
                            access_request = ServiceAccessRequest(resource=resource, user=request.user)
                    elif type == "dataset":
                        resource = Dataset.objects.get(pk=resource_id)
                        if len(DatasetAccessRequest.objects.filter(resource=resource, user=request.user, response_date=None, status='open')) > 0:
                            access_request = DatasetAccessRequest.objects.filter(resource=resource, user=request.user, response_date=None).first()
                            access_request.creation_date = datetime.datetime.now()
                        else:
                            access_request = DatasetAccessRequest(resource=resource, user=request.user)
                    else:
                        raise Exception
                    access_request.save()
                    return HttpResponse('')
                except:
                    response = JsonResponse({"error": "Resource not found."})
                    response.status_code = 404
                    return response
        except:
            traceback.print_exc()
            response = JsonResponse({"error": "Request failed."})
            response.status_code = 500  # To announce that the user isn't allowed to publish
            return response
    else:
        response = JsonResponse({"error": "Permission Denied"})
        response.status_code = 403  # To announce that the user isn't allowed to publish
        return response


def share_access_to_resource(request, type):
    if request.method == "POST" and request.user.is_authenticated():
        try:
            if 'request_id' in request.POST.keys():
                request_id = int(request.POST.get('request_id'))
                try:
                    if type == "dashboard":
                        access_request = DashboardAccessRequest.objects.get(pk=request_id)
                    elif type == "service":
                        access_request = ServiceAccessRequest.objects.get(pk=request_id)
                    elif type == "dataset":
                        access_request = DatasetAccessRequest.objects.get(pk=request_id)
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
                    ra = DashboardAccess(dashboard=resource, user=user)
                ra.can_edit = can_edit
            elif type == "service":
                if len(ServiceAccess.objects.filter(service=resource, user=user)) > 0:
                    ra = ServiceAccess.objects.filter(service=resource, user=user).first()
                else:
                    ra = ServiceAccess(service=resource, user=user)
            elif type == "dataset":
                if len(DatasetAccess.objects.filter(dataset=resource, user=user)) > 0:
                    ra = DatasetAccess.objects.filter(dataset=resource, user=user).first()
                else:
                    ra = DatasetAccess(dataset=resource, user=user)
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

