# if there are less results than `GRANULARITY_MIN_PAGES`
# any granularity requests are ignored
import json

import decimal

import datetime

GRANULARITY_MIN_PAGES = 10000


class ResultEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, float):
            return float(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)
