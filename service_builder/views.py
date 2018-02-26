from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


def index_temp(request):
    return render(request, 'service_builder/index_temp.html', {})
