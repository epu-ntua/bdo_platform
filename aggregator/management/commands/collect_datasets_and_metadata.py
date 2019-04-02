from django.core.management.base import BaseCommand, CommandError
from aggregator.models import *
from django.conf import settings
import prestodb
import psycopg2
import requests
import json
from datetime import datetime

class Command(BaseCommand):
    help = 'Collects the datasets/tables on Presto and updates all the metadata'

    def add_arguments(self, parser):
        parser.add_argument('--update_old', default=False, help='For already added datasets, just update their '
                                                                'variables and dimensions without creating new ones')

    def handle(self, *args, **options):
        # GET JWT for fileHandler
        response = requests.post(settings.PARSER_LOG_IN_URL,
                                 data=json.dumps({"username": settings.PARSER_USERNAME, "password": settings.PARSER_PASSWORD}))
        FILEHANDLER_JWT = response.headers["Authorization"]

        # GET JWT for Harmonization
        headers = {'Content-type': 'application/json'}
        response = requests.post(settings.HARMONIZATION_AUTH,
                                 data=json.dumps({"username": settings.HARMONIZATION_USERNAME, "password": settings.HARMONIZATION_PASSWORD}),
                                 headers=headers)
        self.stdout.write(str(response))
        HARMONIZATION_JWT = str(response.json()["access_token"])

        # GET THE TABLES FROM DJANGO
        all_tables_django = [d['table_name'] for d in Dataset.objects.filter(stored_at='UBITECH_PRESTO').values('table_name')]
        self.stdout.write('tables in django')
        self.stdout.write(str(all_tables_django))
        self.stdout.write(str(len(all_tables_django)))

        # # GET THE TABLES FROM FILEHANDLER PROFILES
        # headers = {'Authorization': FILEHANDLER_JWT}
        # response = requests.get(settings.PROFILES_URL, headers=headers)
        # profile_list = response.json()
        # all_tables_profiles = [profile["storageTable"] for profile in profile_list]
        # self.stdout.write('tables with profiles')
        # self.stdout.write(str(all_tables_profiles))
        # self.stdout.write(str(len(all_tables_profiles)))

        # GET THE TABLES FROM HARMONIZATION PROFILES
        headers = {'Authorization': "JWT " + HARMONIZATION_JWT}
        response = requests.get(settings.HARMONIZATION_DATASET_LIST_URL, headers=headers)
        profile_list = response.json()
        all_tables_profiles = [profile["storageTable"] for profile in profile_list]
        self.stdout.write('tables with profiles')
        self.stdout.write(str(all_tables_profiles))
        self.stdout.write(str(len(all_tables_profiles)))

        # FIND THE TABLES THAT DO NOT EXIST IN DJANGO
        tables_to_add = list(set(all_tables_profiles) - set(all_tables_django))
        self.stdout.write('tables to add')
        self.stdout.write(str(tables_to_add))
        self.stdout.write(str(len(tables_to_add)))

        for i, profile in enumerate(profile_list[:]):
            print "Profile: " + str(i)
            if profile["storageTable"] in tables_to_add:
                dataset = Dataset(title=profile["title"],
                                  source=profile["source"],
                                  stored_at="UBITECH_PRESTO",
                                  table_name=profile["storageTable"],
                                  publisher=profile["publisher"])
                self.stdout.write('adding dataset '+str(dataset.title))
            else:
                # THIS MAY RETURN MORE THAN ONE DATASETS BECAUSE 1 DATASET CAN BE RELATED TO MANY PROFILES
                dataset = Dataset.objects.filter(stored_at="UBITECH_PRESTO", table_name=profile["storageTable"]).first()
                self.stdout.write('modifying dataset ' + str(dataset.title))
            basic_info = ['title', 'source', 'storageTable', 'publisher', 'description', 'spatialEast', 'spatialSouth', 'spatialNorth', 'spatialWest',
                          'temporalCoverageBegin', 'temporalCoverageEnd', 'license', 'observations']
            for field in basic_info:
                try:
                    self.stdout.write('setting' + str(field))
                    setattr(dataset, field, profile[field])
                    dataset.save()
                except Exception, e:
                    setattr(dataset, field, None)
                    dataset.save() 
                    pass
            if profile["accessRights"] == 'Public':
                dataset.private = False
            else:
                dataset.private = True
            metadata = {}
            not_include = basic_info + ["variables", "id", "profileName"]
            for key in profile.keys():
                if key not in not_include:
                    metadata[key] = profile[key]
            dataset.metadata = metadata
            dataset.save()
            possible_dimensions = ["latitude", "longitude", "time", "platform_id", "depth", "manually_entered_depth",
                                   "automatically_measured_latitude", "automatically_measured_longitude", "voyage_number", "trip_identifier",
                                   "timestamp", "ship_id", "ship_name", "imo_id", "mmsi", 'imo']
            possible_vessel_identifiers = ["platform_id", "ship_id", "ship_name", "imo_id", "mmsi", 'imo', "voyage_number", "trip_identifier"]

            ### REMOVE IT
            # column_list_titles = [var["canonicalName"] for var in profile["variables"]]
            # dataset_vessel_identifiers = [col for col in column_list_titles if col in possible_vessel_identifiers]
            ###/ REMOVE IT

            if profile["storageTable"] in tables_to_add:
            # if profile["storageTable"] in tables_to_add and len(dataset_vessel_identifiers)>0:
                dataset_variables = []
                dataset_dimensions = []
                for var in profile["variables"]:
                    if var["canonicalName"] not in possible_dimensions:
                        dataset_variables.append(var)
                    else:
                        dataset_dimensions.append(var)
                # this change was made because i.e. in HCMR Aegean Sea Bathymetry, no variable was present
                if len(dataset_variables) == 0 and 'depth' in [d["canonicalName"] for d in dataset_dimensions]:
                    for d in dataset_dimensions:
                        if d["canonicalName"] == 'depth':
                            dataset_dimensions.remove(d)
                            dataset_variables.append(d)
                self.stdout.write('variables to add')
                self.stdout.write(str(dataset_variables))
                self.stdout.write('dimensions to add')
                self.stdout.write(str(dataset_dimensions))
                for var in dataset_variables:
                    self.stdout.write('adding '+str(var["canonicalName"]))
                    if var["unit"] is None:
                        var["unit"] = ''
                    # GET one variable info
                    headers = {'Authorization': FILEHANDLER_JWT, 'Content-type': 'application/json'}
                    response = requests.post(settings.VARIABLE_LOOKUP_URL,
                                             data=json.dumps([{"name": var["name"], "canonicalName": var["canonicalName"]}]),
                                             headers=headers)
                    if len(response.json()) > 0:
                        var_info = response.json()[0]
                        variable = Variable(name=var_info["canonicalName"], title=var_info["title"], original_column_name=var_info["name"],
                                        unit=var_info["unit"], description=var_info["description"], sameAs=var_info["sameAs"],
                                        dataType=var_info["dataType"], dataset=dataset)
                    else:
                        variable = Variable(name=var["canonicalName"], title=var["name"], original_column_name=var["name"],
                                            unit=var["unit"], dataset=dataset)
                    variable.save()
                    for dim in dataset_dimensions:
                        self.stdout.write('adding ' + str(dim["canonicalName"]))
                        if dim["unit"] is None:
                            dim["unit"] = ''
                        # GET one dimension info
                        headers = {'Authorization': FILEHANDLER_JWT, 'Content-type': 'application/json'}
                        response = requests.post(settings.VARIABLE_LOOKUP_URL,
                                                 data=json.dumps([{"name": dim["name"], "canonicalName": dim["canonicalName"]}]), headers=headers)
                        if len(response.json()) > 0:
                            dim_info = response.json()[0]
                            dimension = Dimension(name=dim_info["canonicalName"], title=dim_info["title"], original_column_name=dim_info["name"],
                                                  unit=dim_info["unit"], description=dim_info["description"], sameAs=dim_info["sameAs"],
                                                  dataType=dim_info["dataType"], variable=variable)
                        else:
                            dimension = Dimension(name=dim["canonicalName"], title=dim["name"], original_column_name=dim["name"],
                                                  unit=dim["unit"], variable=variable)
                        dimension.save()
            else:
                if options['update_old']:
                    possible_dimensions = ["latitude", "longitude", "time", "platform_id", "depth", "manually_entered_depth",
                                           "automatically_measured_latitude", "automatically_measured_longitude", "voyage_number", "trip_identifier",
                                           "timestamp", "ship_id"]
                    dataset_variables = []
                    dataset_dimensions = []
                    for var in profile["variables"]:
                        if var["canonicalName"] not in possible_dimensions:
                            dataset_variables.append(var)
                        else:
                            dataset_dimensions.append(var)
                    for var in dataset_variables:
                        # GET one variable info
                        headers = {'Authorization': FILEHANDLER_JWT, 'Content-type': 'application/json'}
                        response = requests.post(settings.VARIABLE_LOOKUP_URL,
                                                 data=json.dumps([{"name": var["name"], "canonicalName": var["canonicalName"]}]), headers=headers)
                        if len(response.json()) > 0:
                            var_info = response.json()[0]
                            self.stdout.write('modifying '+str(var_info["canonicalName"]))
                            try:
                                variable = Variable.objects.get(dataset=dataset, name=var_info["canonicalName"])
                            except Exception, e:
                                variable = Variable(name=var_info["canonicalName"], title=var_info["title"], original_column_name=var_info["name"],
                                            unit=var_info["unit"], description=var_info["description"], sameAs=var_info["sameAs"],
                                            dataType=var_info["dataType"], dataset=dataset)
                                pass
                            variable.name = var_info["canonicalName"]
                            variable.title = var_info["title"]
                            variable.original_column_name = var_info["name"]
                            variable.unit = var_info["unit"]
                            variable.description = var_info["description"]
                            variable.sameAs = var_info["sameAs"]
                            variable.dataType = var_info["dataType"]
                            variable.save()
                        else:
                            self.stdout.write('modifying ' + str(var["canonicalName"]))
                            try:
                                variable = Variable.objects.get(dataset=dataset, name=var["canonicalName"])
                            except Exception, e:
                                variable = Variable(name=var["canonicalName"], title=var["name"], original_column_name=var["name"],
                                                    unit=var["unit"], dataset=dataset)
                                pass
                            variable.name = var["canonicalName"]
                            variable.title = var["name"]
                            variable.original_column_name = var["name"]
                            variable.unit = var["unit"]
                            variable.save()
                        for dim in dataset_dimensions:
                            # GET one dimension info
                            headers = {'Authorization': FILEHANDLER_JWT, 'Content-type': 'application/json'}
                            response = requests.post(settings.VARIABLE_LOOKUP_URL,
                                                     data=json.dumps([{"name": dim["name"], "canonicalName": dim["canonicalName"]}]), headers=headers)
                            if len(response.json()) > 0:
                                dim_info = response.json()[0]
                                try:
                                    dimension = Dimension.objects.get(variable=variable, name=dim_info["canonicalName"])
                                except Exception, e:
                                    dimension = Dimension(name=dim_info["canonicalName"], title=dim_info["title"], original_column_name=dim_info["name"],
                                                  unit=dim_info["unit"], description=dim_info["description"], sameAs=dim_info["sameAs"],
                                                  dataType=dim_info["dataType"], variable=variable)
                                    pass
                                dimension.name = dim_info["canonicalName"]
                                dimension.title = dim_info["title"]
                                dimension.original_column_name = dim_info["name"]
                                dimension.unit = dim_info["unit"]
                                dimension.description = dim_info["description"]
                                dimension.sameAs = dim_info["sameAs"]
                                dimension.dataType = dim_info["dataType"]
                                dimension.save()
                            else:
                                try:
                                    dimension = Dimension.objects.get(variable=variable, name=dim["canonicalName"])
                                except Exception, e:
                                    dimension = Dimension(name=dim["canonicalName"], title=dim["name"],
                                                          original_column_name=dim["name"],
                                                          unit=dim["unit"], variable=variable)
                                    pass
                                dimension.name = dim["canonicalName"]
                                dimension.title = dim["name"]
                                dimension.original_column_name = dim["name"]
                                dimension.unit = dim["unit"]
                                dimension.save()

            headers = {'Authorization': FILEHANDLER_JWT, 'Content-type': 'application/json'}
            response = requests.get(settings.PARSER_URL + '/fileHandler/table/' + dataset.table_name + '/lastUpdate', headers=headers)
            if response.content == '':
                dataset.last_updated = None
                dataset.save()
            else:
                dataset.last_updated = datetime.strptime(response.content, '%Y-%m-%dT%H:%M:%S.%f')
                dataset.save()
            if profile["storageTable"] in tables_to_add:
            # if 1 == 1:
                rows_to_render = []
                variable_list_canonical = [v.safe_name for v in Variable.objects.filter(dataset=dataset)]
                variable_list_titles = [v.title for v in Variable.objects.filter(dataset=dataset)]
                variable_list_units = [v.unit for v in Variable.objects.filter(dataset=dataset)]
                dimension_list_canonical = [d.name for d in Dimension.objects.filter(variable=Variable.objects.filter(dataset=dataset)[0])]
                dimension_list_titles = [d.title for d in Dimension.objects.filter(variable=Variable.objects.filter(dataset=dataset)[0])]
                dimension_list_units = [d.unit for d in Dimension.objects.filter(variable=Variable.objects.filter(dataset=dataset)[0])]
                column_list_canonical = variable_list_canonical + dimension_list_canonical
                column_list_titles = variable_list_titles + dimension_list_titles
                column_list_units = variable_list_units + dimension_list_units
                column_list_string = ""
                for column in column_list_canonical:
                    column_list_string += ", " + column
                column_list_string = column_list_string[1:]
                column_list_filter_string = ""
                for column in column_list_canonical[:5]:
                    column_list_filter_string += "AND " + column + " is not NULL "
                # column_list_filter_string = column_list_filter_string[4:]
                try:
                    presto_credentials = settings.DATABASES['UBITECH_PRESTO']
                    conn_presto = prestodb.dbapi.connect(
                        host=presto_credentials['HOST'],
                        port=presto_credentials['PORT'],
                        user=presto_credentials['USER'],
                        catalog=presto_credentials['CATALOG'],
                        schema=presto_credentials['SCHEMA'],
                    )
                    cursor_presto = conn_presto.cursor()
                    query = "SELECT " + column_list_string + " FROM " + str(dataset.table_name) + " WHERE " + column_list_filter_string + " LIMIT 5"
                    print query
                    cursor_presto.execute(query)
                    rows_to_render = cursor_presto.fetchall()
                    sample_rows = []
                    for row in rows_to_render:
                        sample_row = []
                        for x in row:
                            if isinstance(x, unicode):
                                y = x.encode('ascii', 'backslashreplace')
                            else:
                                y = x
                            sample_row.append(y)
                        sample_rows.append(sample_row)
                    print rows_to_render
                    dataset.sample_rows = {"column_titles": column_list_titles,
                                           "column_units": column_list_units,
                                           "data": sample_rows}
                    dataset.save()

                except Exception, e:
                    print 'error'
                    print str(e)
                    pass

            if response.content != '' or profile["storageTable"] in tables_to_add:
                try:
                    presto_credentials = settings.DATABASES['UBITECH_PRESTO']
                    conn_presto = prestodb.dbapi.connect(
                        host=presto_credentials['HOST'],
                        port=presto_credentials['PORT'],
                        user=presto_credentials['USER'],
                        catalog=presto_credentials['CATALOG'],
                        schema=presto_credentials['SCHEMA'],
                    )
                    cursor_presto = conn_presto.cursor()
                    query = "SELECT COUNT(*) FROM " + str(dataset.table_name)
                    print query
                    cursor_presto.execute(query)
                    number_of_rows = cursor_presto.fetchall()[0][0]
                    print number_of_rows
                    dataset.number_of_rows = number_of_rows
                    dataset.save()
                except Exception, e:
                    print 'error'
                    print str(e)
                    pass
        self.stdout.write(self.style.SUCCESS('Successfully collected and updated datasets and metadata'))
