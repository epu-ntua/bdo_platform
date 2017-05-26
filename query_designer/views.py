# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bson import ObjectId
from django.http import JsonResponse
from django.shortcuts import render

from mongo_client import get_mongo_db, MongoResponse


from query_designer.postgres_api import *
from query_designer.postgres_query import *

# from query_designer.mongo_api import *
# from query_designer.mongo_query import *


def index(request):
    return render(request, 'query_designer/index.html', {
        'sidebar_active': 'queries',
    })

