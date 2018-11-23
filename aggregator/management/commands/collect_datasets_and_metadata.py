from django.core.management.base import BaseCommand, CommandError
from aggregator.models import *
from django.conf import settings
import prestodb
import psycopg2
import requests
import json

class Command(BaseCommand):
    help = 'Collects the datasets/tables on Presto and updates all the metadata'

    def handle(self, *args, **options):
        # GET JWT
        response = requests.post(settings.PARSER_LOG_IN_URL,
                                 data=json.dumps({"username": settings.PARSER_USERNAME, "password": settings.PARSER_PASSWORD}))
        FILEHANDLER_JWT = response.headers["Authorization"]
        # GET THE TABLES FROM DJANGO
        all_tables_django = [d['table_name'] for d in Dataset.objects.filter(stored_at='UBITECH_PRESTO').values('table_name')]
        self.stdout.write('tables in django')
        self.stdout.write(str(all_tables_django))
        self.stdout.write(str(len(all_tables_django)))

        # GET THE TABLES FROM METADATA PROFILES
        headers = {'Authorization': FILEHANDLER_JWT}
        response = requests.get(settings.PROFILES_URL, headers=headers)
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

        for profile in profile_list:
            if profile["storageTable"] in tables_to_add:
                dataset = Dataset(title=profile["title"],
                                  source=profile["source"],
                                  stored_at="UBITECH_PRESTO",
                                  table_name=profile["storageTable"],
                                  publisher=profile["publisher"])
                self.stdout.write('adding dataset '+str(dataset.title))
            else:
                # THIS MAY RETURN MORE THAN ONE DATASETS BECAUSE 1 DATASET CAN BE RELATED TO MANY PROFILES
                dataset = Dataset.objects.get(stored_at="UBITECH_PRESTO", table_name=profile["storageTable"])
                self.stdout.write('modifying dataset ' + str(dataset.title))
            basic_info = ['title', 'source', 'storageTable', 'publisher', 'description', 'spatialEast', 'spatialSouth', 'spatiaNorth', 'spatialWest',
                          'temporalCoverageBegin', 'temporalCoverageEnd', 'license', 'observation']
            for field in basic_info:
                try:
                    setattr(dataset, field, profile[field])
                except:
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

            if profile["storageTable"] in tables_to_add:
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
                self.stdout.write('variables to add')
                self.stdout.write(str(dataset_variables))
                self.stdout.write('dimensions to add')
                self.stdout.write(str(dataset_dimensions))
                for var in dataset_variables:
                    self.stdout.write('adding '+str(var["canonicalName"]))
                    if var["unit"] is None:
                        var["unit"] = ''
                    variable = Variable(name=var["canonicalName"], title=var["name"], unit=var["unit"], dataset=dataset)
                    variable.save()
                    for dim in dataset_dimensions:
                        self.stdout.write('adding ' + str(dim["canonicalName"]))
                        if dim["unit"] is None:
                            dim["unit"] = ''
                        dimension = Dimension(name=dim["canonicalName"], title=dim["name"], unit=dim["unit"], variable=variable)
                        dimension.save()

        self.stdout.write(self.style.SUCCESS('Successfully collected and updated datasets and metadata'))
