from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from query_designer.models import Query
from visualizer.models import Visualization
from dashboard_builder.models import Dashboard

from . import forms

import json

def build_dynamic_dashboard(request):
    if request.method == 'GET':
        user = request.user
        if request.user.is_authenticated():
            saved_queries = Query.objects.filter(user=user).exclude(document__from=[])
        else:
            saved_queries = []
        num_of_dashboards = Dashboard.objects.count()
        toCreate = request.GET.get('toCreate', 'empty')
        form_class = forms.CkEditorForm
        return render(request, 'dashboard_builder/dashboard_builder2.html', {
            'dashboard_title': num_of_dashboards+1,
            'sidebar_active': 'products',
            'saved_queries': saved_queries,
            'available_viz': Visualization.objects.filter(hidden=False).order_by('id'),
            'form_class': form_class,
            'components': Visualization.objects.all().order_by('id'),
            'form': form_class,
            'toCreate': toCreate,
        })
    return None


def get_visualization_form_fields(request):
    viz_id = request.GET.get('id')
    order = request.GET.get('order')
    visualization = Visualization.objects.get(pk=viz_id)
    html = render_to_string('dashboard_builder/config-visualization-form-fields.html', {'order': order,
                                                                                        'viz_id': viz_id,
                                                                                        'info': visualization.info,
                                                                                        'action': visualization.view_name})
    return HttpResponse(html)


def get_visualization_form_fields_df(request):
    viz_id = request.GET.get('id')
    order = request.GET.get('order')
    visualization = Visualization.objects.get(pk=viz_id)
    html = render_to_string('dashboard_builder/config-visualization-form-fields-df.html', {'order': order,
                                                                                        'viz_id': viz_id,
                                                                                        'info': visualization.info,
                                                                                        'action': visualization.view_name})
    return HttpResponse(html)


def save_dashboard(request, pk=None):
    # create or update
    if not pk:
        user = request.user
        if user.is_authenticated():
            dashboard = Dashboard(user=user)
        else:
            dashboard = Dashboard(user=User.objects.get(username='BigDataOcean'))

    else:
        dashboard = Dashboard.objects.get(pk=pk)

    dashboard.title = 'BDO Dashboard'
    print request.POST
    dashboard_data = request.POST.dict()
    for order in dashboard_data.keys():
        dashboard_data = json.loads(order)
    # for k in dashboard_data.keys():
    #     dashboard_data = k
    #     break
    #
    # json_acceptable_string = dashboard_data.replace("'", "\"")
    # print "NOW PRINTING json_acceptable_string"
    # print json_acceptable_string
    # dashboard_data = json.loads(json_acceptable_string)
    print "We are now printing dashboard data"
    print dashboard_data
    print "end of data"
    title = dashboard_data.pop('title', None)
    private = dashboard_data.pop('private', None)

    for order in dashboard_data.keys():
        print order
        print dashboard_data[order]
    dashboard.viz_components = dashboard_data
    dashboard.title = title
    dashboard.private = private
    print dashboard.title

    dashboard.save()

    return JsonResponse({
        'pk': dashboard.pk,
    })

def edit_dashboard(request, pk= None):
    if request.method == 'GET':
        user = request.user
        if request.user.is_authenticated():
            saved_queries = Query.objects.filter(user=user).exclude(document__from=[])
        else:
            saved_queries = []

        toCreate = "None"
        form_class = forms.CkEditorForm

        dashboard = Dashboard.objects.get(pk=pk)
        return render(request, 'dashboard_builder/dashboard_editor.html', {
            'dashboard': dashboard,
            'dashboard_pk': pk,
            'dashboard_title': dashboard.title,
            'sidebar_active': 'products',
            'saved_queries': saved_queries,
            'components': Visualization.objects.all().order_by('id'),
            'form': form_class,
            'toCreate': toCreate,
        })
    return None
