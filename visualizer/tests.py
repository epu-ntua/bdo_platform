from django.test import TestCase

from visualizer.models import Visualization
from query_designer.models import AbstractQuery
from aggregator.models import *
import json
from django.test import Client

class TestVisualizationCreation(TestCase) :

    def test_chart_visualization(self):
        user = User(username='testuser_v')
        user.save()
        cl = Client()
        cl.force_login(user)
        viz_title = 'Line Chart'
        viz_desc = 'A Line Chart Description'
        viz_hidden = False
        viz_info = {"arguments": [{"name": "y_var", "type": "VARIABLE_LIST", "title": "Y-Axis Variable",
                                   "description":  "The variable(s) presented on the Y-Axis of the Line Chart."},
                                  {"name": "x_var", "type": "COLUMN", "title": "X-Axis Variable", "description":
                                      "The variable or dimension presented on the X-Axis of the Line Chart."},
                                  {"name": "agg_func", "type": "AGG_FUNCTION", "title": "Aggregate Function",
                                   "default": "avg", "description": "The function used for aggregating the data."}]}
        viz_view_name = 'get_line_chart_am'
        viz_icon = 'fas fa-chart-line'
        viz_type = 'chart'
        viz_order = 1
        viz_data_source = 'query'
        visualization = Visualization(title=viz_title, description=viz_desc, hidden=viz_hidden, info=viz_info,
                                      view_name=viz_view_name, icon=viz_icon, type=viz_type,
                                      order=viz_order)
        visualization.save()
        viz_id = visualization.id

        org_title = 'NESTER'
        org_desc = ''
        organization = Organization(title=org_title, description=org_desc)
        organization.save()
        dataset_name = 'maretec_waves_forecast'
        dataset_title = 'Maretec Waves Forecast'
        dataset = Dataset(title=dataset_title, stored_at="UBITECH_PRESTO", table_name=dataset_name,
                          organization=organization)
        dataset.save()
        dataset_id = dataset.id

        variable_name = 'sea_surface_wave_significant_height'
        variable_title = 'Sea surface wave significant height'
        variable = Variable(name=variable_name, title=variable_title, dataset_id=dataset_id, cell_methods='{}')
        variable.save()
        variable_id = variable.id

        dimension_time_title = 'Time'
        dimension_time_name = 'time'
        dim_time = Dimension(name=dimension_time_name, title=dimension_time_title, variable_id=variable_id)
        dim_time.save()
        dim_time_id = dim_time.id

        dimension_lat_title = 'Latitude'
        dimension_lat_name = 'latitude'
        dim_lat = Dimension(name=dimension_lat_name, title=dimension_lat_title, variable_id=variable_id)
        dim_lat.save()
        dim_lat_id = dim_lat.id

        dimension_lon_title = 'Longitude'
        dimension_lon_name = 'longitude'
        dim_lon = Dimension(name=dimension_lon_name, title=dimension_lon_title, variable_id=variable_id)
        dim_lon.save()
        dim_lon_id = dim_lon.id

        doc_str = {"from":
                       [{"name": dataset_name,
                         "type": str(variable_id),
                         "select": [
                             {"name": "i0_" + variable_name,
                              "type": "VALUE",
                              "title": dataset_title,
                              "exclude": False, "groupBy": False,
                              "aggregate": "AVG"},
                             {"name": "i0_" + str(dimension_time_name),
                              "type": str(dim_time_id),
                              "title": dimension_time_title,
                              "exclude": False,
                              "groupBy": True,
                              "aggregate": "date_trunc_minute"}
                             ,
                             {"name": "i0_" + str(dimension_lat_name),
                              "type": str(dim_lat_id),
                              "title": dimension_lat_title,
                              "exclude": False,
                              "groupBy": True,
                              "aggregate": "round2"},
                             {"name": "i0_" + str(dimension_lon_name),
                              "type": str(dim_lon_id),
                              "title": dimension_lon_title,
                              "exclude": False,
                              "groupBy": True,
                              "aggregate": "round2"}
                         ]}
                        ],
                   "limit": 500,
                   "offset": 0,
                   "filters":
                       {"a": "<" + str(dim_lat_id) + "," + str(dim_lon_id) + ">",
                        "b": "<<30,6>,<46,36>>",
                        "op": "inside_rect"},
                   "distinct": False,
                   "orderings": []
                   }
        abstract_query = AbstractQuery(document=doc_str, user=user)
        abstract_query.save()
        query_id = abstract_query.id
        from time import time
        viz_timestamp = str(time()).replace('.', '')

        url_viz_string = '/visualizations/' + str(viz_view_name) + '/?' + 'viz_id=' + str(viz_id) + '&action=' + \
                         str(viz_view_name) + '&y_var%5B%5D=i0_' + str(variable_name) + '&x_var=i0_' + \
                         str(dimension_time_name) + '&agg_func=AVG&query=' + str(query_id) + '&timestamp=' + \
                         str(viz_timestamp)

        # payload = {"viz_id": str(viz_id), "action": str(viz_view_name), "y_var": ('i0_' + str(variable_name)),
        #            "x_var": 'i0_' + str(dimension_time_name), "agg_func": "AVG", "query": str(query_id), "timestamp":
        #                str(viz_timestamp)}
        # payload = json.dumps(payload)
        # payloadContainer = {payload: ''}
        #
        # cl = Client()
        # url = "http://localhost:8000/visualizations/" + str(viz_view_name)

        # response = cl.get(url, data=payloadContainer)
        response = cl.get(url_viz_string)

        # check if 200 status code is returned
        self.assertEqual(response.status_code, 200)
        # check if the html has the correct url

        self.assertEqual(response.context[0]['request'].get_full_path().strip(),
                         str(url_viz_string).strip())
        self.assertEqual(response.context[0]['isDate'], str('true'))
        self.assertEqual(response.context[0]['min_period'], str('ss'))
        self.assertEqual(response.context[0]['value_col'][0][0], 'i0_' + str(variable_name))
        self.assertEqual(response.context[0]['category_col'], 'i0_' + str(dimension_time_name))
        from bs4 import BeautifulSoup

        # check if it is valid html
        soup = BeautifulSoup(response.content, 'html.parser')

        bool_soup = bool(soup.find())
        self.assertEqual(str(bool_soup), str(True))















def filldate(date, mode):
    date = date.split(" ")
    time = []
    if len(date) > 1:
        time = date[1].split(':')
    date = date[0].split('-')
    if len(date) == 1:
        newdate = date[0]
        if mode == 'min':
            newdate = newdate + "-01-01 00:00:00"
        else:
            newdate = newdate + "-12-31 23:59:59"
    elif len(date) == 2:
        newdate = date[0] + "-" + date[1]
        if mode == 'min':
            newdate = newdate + "-01 00:00:00"
        else:
            newdate = newdate + "-31 23:59:59"
    else:
        newdate = date[0] + "-" + date[1] + "-" + date[2] + " "
        if len(time) == 0:
            if mode == 'min':
                newdate = newdate + "00:00:00"
            else:
                newdate = newdate + "23:59:59"
        elif len(time) == 1:
            if mode == 'min':
                newdate = newdate + time[0] + ":00:00"
            else:
                newdate = newdate + time[0] + ":59:59"
        else :
            if mode == 'min':
                newdate = newdate + time[0] + ":" + time[1] + ":00"
            else:
                newdate = newdate + time[0] + ":" + time[1] + ":59"

    return newdate

def get_data(query_pk, markers, ship, mindate, maxdate):
    q = Query.objects.get(pk=query_pk)
    q = Query(document=q.document)
    q.document['limit'] = markers
    filters = {}
    mindate = filldate(mindate, "min")
    maxdate = filldate(maxdate, "max")

    mindate = datetime.strptime(mindate, '%Y-%m-%d %H:%M:%S')
    maxdate = datetime.strptime(maxdate, '%Y-%m-%d %H:%M:%S')
    if ship != 'all':
        filters = {"a": "i0_ship_id", "b": ship, "op": "eq"}
        #q.document["filters"] = {"a": "i0_timestamp", "b": mindate, "op": "gt"}
        #q.document["filters"] = {"a": "i0_timestamp", "b": maxdate, "op": "lt"}
    q.document['filters'] = filters

    result = q.execute()[0]['results']
    print result[:3]

    result_headers = q.execute(only_headers=True)[0]['headers']
    for idx, c in enumerate(result_headers['columns']):
        if str(c['name']).find('lat') >= 0:
            lat_index = idx
        elif str(c['name']).find('lon') >= 0:
            lon_index = idx
        elif str(c['name']).find('ship') >= 0:
            ship_index = idx
        elif str(c['name']).find('timestamp') >= 0:
            time_index = idx
        elif str(c['isVariable']) == 'True':
            var_index = idx

    print result_headers, lat_index, lon_index, ship_index, time_index, var_index

    return {"data": result, "var": var_index, "ship": ship_index, "time": time_index, "lat": lat_index, "lon": lon_index}
