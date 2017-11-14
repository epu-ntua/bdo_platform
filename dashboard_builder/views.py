from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from query_designer.models import Query
from visualizer.models import Visualization


def build_dynamic_dashboard(request):
    if request.method == 'GET':
        user = request.user
        if request.user.is_authenticated():
            saved_queries = Query.objects.filter(user=user)
        else:
            saved_queries = []
        return render(request, 'dashboard_builder/dashboard_builder.html', {
            'sidebar_active': 'products',
            'saved_queries': saved_queries,
            'components': Visualization.objects.all().order_by('id'),
        })
    return None


def get_visualization_form_fields(request):
    viz_id = request.GET.get('id')
    order = request.GET.get('order')
    visualization = Visualization.objects.get(pk=viz_id)
    html = render_to_string('dashboard_builder/config-visualization-form-fields.html', {'order': order, 'viz_id': viz_id, 'info': visualization.info})
    return HttpResponse(html)
