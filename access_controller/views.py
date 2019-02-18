# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.exceptions import PermissionDenied, ValidationError
from dashboard_builder.models import Dashboard, DashboardAccess, DashboardAccessRequest
import datetime
import traceback
from django.http import HttpResponse, JsonResponse


def requests(request):
    my_requests_dashboard_view = DashboardAccessRequest.objects.filter(user=request.user)
    return render(request, 'access_controller/requests_page.html', {
        'my_requests_dashboard_view': my_requests_dashboard_view
    })


def share_access_to_dashboard(request):
    if request.method == "POST" and request.user.is_authenticated():
        try:
            dashboard_id = int(request.POST.get('dashboard_id'))
            username_or_email = str(request.POST.get('username_or_email'))
            can_edit = str(request.POST.get('can_edit')) == 'true'
            try:
                dashboard = Dashboard.objects.get(pk=dashboard_id)
            except:
                response = JsonResponse({"error": "Dashboard not found."})
                response.status_code = 404
                return response

            try:
                user = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
            except:
                response = JsonResponse({"error": "User not found."})
                response.status_code = 404
                return response

            if len(DashboardAccess.objects.filter(dashboard=dashboard, user=user)) > 0:
                da = DashboardAccess.objects.filter(dashboard=dashboard, user=user).first()
                da.start = datetime.datetime.now()
                da.end = datetime.datetime.now() + datetime.timedelta(days=365)
                da.can_edit = can_edit
                da.valid = True
            else:
                da = DashboardAccess(dashboard=dashboard, user=user, start=datetime.datetime.now(),
                                     end=datetime.datetime.now() + datetime.timedelta(days=365), can_edit=can_edit, valid=True)
            da.save()
            return HttpResponse('')
        except:
            traceback.print_exc()
            response = JsonResponse({"error": "Dashboard sharing failed."})
            response.status_code = 500  # To announce that the user isn't allowed to publish
            return response

    else:
        response = JsonResponse({"error": "Permission Denied"})
        response.status_code = 403  # To announce that the user isn't allowed to publish
        return response
