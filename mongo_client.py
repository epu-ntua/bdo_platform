import json

from datetime import datetime
from django.http import HttpResponse

from bson import ObjectId
from json import JSONEncoder
from pymongo import MongoClient
from pymongo.cursor import Cursor

from bdo_platform.settings_management.development_dpap import DOCUMENT_STORE_URL, DOCUMENT_STORE_DB


def get_mongo_db():
    return MongoClient(DOCUMENT_STORE_URL).get_database(name=DOCUMENT_STORE_DB)


class MongoEncoder(JSONEncoder):

    def default(self, obj, **kwargs):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat(sep='T')
        else:
            return JSONEncoder.default(self, obj, **kwargs)


class MongoResponse(HttpResponse):
    """
    An HTTP response class that consumes data to be serialized to JSON.

    :param data: Data to be dumped into json. By default only ``dict`` objects
      are allowed to be passed due to a security flaw before EcmaScript 5. See
      the ``safe`` parameter for more information.
    :param encoder: Should be an json encoder class. Defaults to
      ``django.core.serializers.json.DjangoJSONEncoder``.
    :param safe: Controls if only ``dict`` objects may be serialized. Defaults
      to ``True``.
    :param json_dumps_params: A dictionary of kwargs passed to json.dumps().
    """

    def __init__(self, data, encoder=MongoEncoder, safe=True,
                 json_dumps_params=None, **kwargs):
        if safe and not isinstance(data, dict):
            raise TypeError(
                'In order to allow non-dict objects to be serialized set the '
                'safe parameter to False.'
            )
        if json_dumps_params is None:
            json_dumps_params = {}
        kwargs.setdefault('content_type', 'application/json')
        data = json.dumps(data, cls=encoder, **json_dumps_params)
        super(MongoResponse, self).__init__(content=data, **kwargs)
