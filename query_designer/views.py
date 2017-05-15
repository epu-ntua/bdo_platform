# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bson import ObjectId
from django.http import JsonResponse
from django.shortcuts import render

from mongo_client import get_mongo_db, MongoResponse


def index(request):
    return render(request, 'query_designer/index.html', {

    })


from postgres_api import *



