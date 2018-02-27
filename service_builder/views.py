from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from query_designer.models import Query


def create_new_service(request):
    user = request.user
    if request.user.is_authenticated():
        saved_queries = Query.objects.filter(user=user).exclude(document__from=[])
    else:
        saved_queries = []
    return render(request, 'service_builder/create_new_service.html', {
        'saved_queries': saved_queries, })
