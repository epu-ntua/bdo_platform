# if there are less results than `GRANULARITY_MIN_PAGES`
# any granularity requests are ignored
import json

import decimal

import datetime

GRANULARITY_MIN_PAGES = 10000


class ResultEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        try:
            self.mode = kwargs.pop('mode')
        except:
            pass

        super(ResultEncoder, self).__init__(*args, **kwargs)

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, float):
            return float(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat() + ('Z' if self.mode == 'solr' else '')

        return json.JSONEncoder.default(self, obj)


class PostgresResultEncoder(ResultEncoder):
    mode = 'postgres'


class SolrResultEncoder(ResultEncoder):
    mode = 'solr'

class PrestoResultEncoder(ResultEncoder):
    mode = 'presto'
