# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools
from django.http import JsonResponse
from django.shortcuts import render
from mongo_client import get_mongo_db, MongoResponse

import json
from bson import ObjectId


def home(request):
    return render(request, 'index.html')

from postgres_query import *

