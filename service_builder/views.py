import json

from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from query_designer.models import Query
from visualizer.utils import create_zep__query_paragraph, run_zep_paragraph


def create_new_service(request):
    user = request.user
    if request.user.is_authenticated():
        saved_queries = Query.objects.filter(user=user).exclude(document__from=[])
    else:
        saved_queries = []
    return render(request, 'service_builder/create_new_service.html', {
        'saved_queries': saved_queries,
        'notebook_id': '2D9E8JBBX'})


def load_query(request):
    notebook_id = str(request.GET.get('notebook_id'))
    query_id = int(request.GET.get('query_id'))

    raw_query = Query.objects.get(pk=query_id).raw_query
    query_paragraph_id = create_zep__query_paragraph(notebook_id, 'query paragraph', raw_query)
    run_zep_paragraph(notebook_id, query_paragraph_id)

    result = {}
    # return the found variables
    return HttpResponse(json.dumps(result), content_type="application/json")
