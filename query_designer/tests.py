# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import prestodb
from django.test import TestCase
from query_designer.models import *
from aggregator.models import *
from decimal import *
from django.conf import settings


class QueryDesignerTests(TestCase):

    def test_query_creation(self):

        org_title = 'NESTER'
        org_desc = ''
        organization = Organization(title=org_title, description=org_desc)
        organization.save()
        dataset_name = 'maretec_waves_forecast'
        dataset_title = 'Maretec Waves Forecast'
        dataset = Dataset(title=dataset_title, stored_at="UBITECH_PRESTO", table_name=dataset_name, organization=organization)
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
        dim_lat = Dimension( name=dimension_lat_name, title=dimension_lat_title, variable_id=variable_id)
        dim_lat.save()
        dim_lat_id = dim_lat.id

        dimension_lon_title = 'Longitude'
        dimension_lon_name = 'longitude'
        dim_lon = Dimension( name=dimension_lon_name, title=dimension_lon_title, variable_id=variable_id)
        dim_lon.save()
        dim_lon_id = dim_lon.id


        doc_str = {"from":
                           [{"name": dataset_name,
                             "type": str(variable_id),
                             "select": [
                                 {"name": "i0_"+variable_name,
                                 "type": "VALUE",
                                 "title": dataset_title,
                                 "exclude": False, "groupBy": False,
                                 "aggregate": "AVG"},
                                 {"name": "i0_"+str(dimension_time_name),
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
                           {"a": "<"+str(dim_lat_id)+","+str(dim_lon_id)+">",
                            "b": "<<30,6>,<46,36>>",
                            "op": "inside_rect"},
                       "distinct": False,
                       "orderings": []
                       }
        abstract_query = AbstractQuery(document=doc_str)

        for v in Variable.objects.all():
            print '-'
            print v
        print Variable.objects.get(pk=int(abstract_query.document['from'][0]['type']))
        string_query = abstract_query.raw_query
        expected_string = u"SELECT * FROM (SELECT AVG(" + str(dataset_name) + "." + variable_name + ") AS i0_" + str(
            variable_name) + ",date_trunc('minute', " + str(dataset_name) + "." + str(
            dimension_time_name) + ") AS i0_" + str(dimension_time_name)+ ",round(" + str(dataset_name) + "." + str(
            dimension_lat_name) + ", 2) AS i0_" + dimension_lat_name + ",round(" + str(dataset_name) + "." + str(
            dimension_lon_name) + ", 2) AS i0_" + str(
            dimension_lon_name) + "\nFROM " + str(
            dataset_name) + " \nWHERE " + str(dataset_name) + "." + str(dimension_lat_name) + " >= 30 AND " + str(
            dataset_name) + "." + str(dimension_lat_name) + " <= 46 AND " + str(dataset_name) + "." + str(
            dimension_lon_name) + " >= 6 AND " + str(dataset_name) + "." + str(
            dimension_lon_name) + " <= 36 \nGROUP BY round(" + str(dataset_name) + "." + str(
            dimension_lon_name) + ", 2)" + ",round(" + str(
            dataset_name) + "." + str(dimension_lat_name) + ", 2)"+ ",date_trunc('minute', "+ str(dataset_name) + "." \
                          + str(dimension_time_name) +")\n) AS SQ1\nLIMIT 500"
        print expected_string
        print string_query
        self.assertEqual(string_query.strip(), expected_string.strip())

    def test_query_with_json_document(self):
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
        abstract_query = AbstractQuery(document=doc_str)

        # print abstract_query.document['from'][0]['type']
        # import pdb
        # pdb.set_trace()
        for v in Variable.objects.all():
            print '-'
            print v
        print Variable.objects.get(pk=int(abstract_query.document['from'][0]['type']))
        query= u"SELECT * FROM (SELECT AVG(" + str(dataset_name) + "." + variable_name + ") AS i0_" + str(
            variable_name) + ",date_trunc('minute', " + str(dataset_name) + "." + str(
            dimension_time_name) + ") AS i0_" + str(dimension_time_name) + ",round(" + str(dataset_name) + "." + str(
            dimension_lat_name) + ", 2) AS i0_" + dimension_lat_name + ",round(" + str(dataset_name) + "." + str(
            dimension_lon_name) + ", 2) AS i0_" + str(
            dimension_lon_name) + "\nFROM " + str(
            dataset_name) + " \nWHERE " + str(dataset_name) + "." + str(dimension_lat_name) + " >= 30 AND " + str(
            dataset_name) + "." + str(dimension_lat_name) + " <= 46 AND " + str(dataset_name) + "." + str(
            dimension_lon_name) + " >= 6 AND " + str(dataset_name) + "." + str(
            dimension_lon_name) + " <= 36 \nGROUP BY round(" + str(dataset_name) + "." + str(
            dimension_lon_name) + ", 2)" + ",round(" + str(
            dataset_name) + "." + str(dimension_lat_name) + ", 2)" + ",date_trunc('minute', " + str(dataset_name) + "." \
                          + str(dimension_time_name) + ")\n) AS SQ1\nLIMIT 500"

        print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'


        print settings.DATABASES
        response, encoder = abstract_query.execute()

        # Check if response is in JSON format
        try:
            string_response = json.dumps(response)
            json_object = json.loads(string_response)
            json_flag = True
        except:
            json_flag = False
        self.assertEqual(json_flag, True)


        # check headers from returned data
        input_json_list = []
        for i in doc_str['from'][0]['select']:
            input_json_list.append(i['name'])
        input_json_list.sort()

        output_json_list = []
        for i in response['headers']['columns']:
            output_json_list.append(i['name'])
        output_json_list.sort()

        self.assertEqual(input_json_list, output_json_list)

        # check if data returned is correct

        data = response['results']
        expected_data = []
        cursor = get_presto_cursor()
        cursor.execute(query)
        expected_data = cursor.fetchall()

        self.assertEqual(data, expected_data)

def get_presto_cursor():
    presto_credentials = settings.DATABASES['UBITECH_PRESTO']
    conn = prestodb.dbapi.connect(
        host=presto_credentials['HOST'],
        port=presto_credentials['PORT'],
        user=presto_credentials['USER'],
        catalog=presto_credentials['CATALOG'],
        schema=presto_credentials['SCHEMA'],
    )
    cursor = conn.cursor()
    return cursor