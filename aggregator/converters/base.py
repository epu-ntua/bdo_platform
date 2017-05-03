import json
import os

import decimal

import numpy

from bdo_platform.settings import DATASET_DIR


class BaseVariable(object):
    name = ''
    title = ''
    unit = None

    def to_json(self):
        return {
            'name': self.name,
            'title': self.title,
            'unit': self.unit,
        }


class Dimension(BaseVariable):
    min = None
    max = None
    step = 1
    axis = None

    def to_json(self):
        document = super(Dimension, self).to_json()

        document.update({
            'min': self.min,
            'max': self.max,
            'step': self.step,
            'axis': self.axis,
        })

        return encode_document(document)


class Variable(BaseVariable):
    scale_factor = 1
    add_offset = 0
    cell_methods = []
    dimensions = []
    type_of_analysis = None
    extra_info = {}

    def to_json(self):
        document = super(Variable, self).to_json()

        document.update({
            'scale_factor': self.scale_factor,
            'add_offset': self.add_offset,
            'cell_methods': self.cell_methods,
            'type_of_analysis': self.type_of_analysis,
            'extra_info': self.extra_info,
            'dimensions': self.dimensions,
        })

        return encode_document(document)


class DatasetInfo(object):
    title = ''
    source = ''
    description = ''
    references = []

    def to_json(self):
        return encode_document({
            'title': self.title,
            'source': self.source,
            'description': self.description,
            'references': self.references,
        })


def encode_document(obj):
    for key in obj.keys():
        if isinstance(obj[key], numpy.integer):
            obj[key] = int(obj[key])
        elif isinstance(obj[key], numpy.floating):
            obj[key] = float(obj[key])
        elif isinstance(obj[key], numpy.ndarray):
            obj[key] = obj[key].tolist()

    return obj


class BaseConverter(object):
    name = None
    _dataset = None
    _variables = []
    _dimensions = []
    _data = []

    @property
    def dataset(self):
        raise NotImplementedError('`dataset` getter was not implemented')

    @property
    def variables(self):
        raise NotImplementedError('`variables` getter was not implemented')

    @property
    def dimensions(self):
        raise NotImplementedError('`dimensions` getter was not implemented')

    def data(self, v_name):
        raise NotImplementedError('variable `data` getter was not implemented')

    def get_variable(self, v_name):
        try:
            return [v for v in self.variables if v.name == v_name][0]
        except IndexError:
            return None

    def get_dimension(self, d_name):
        try:
            return [d for d in self.dimensions if d.name == d_name][0]
        except IndexError:
            return None

    @staticmethod
    def full_input_path(filename=None):
        source_path = DATASET_DIR + 'source\\'
        if not os.path.isdir(source_path):
            os.mkdir(source_path)

        if filename is None:
            return source_path

        return os.path.join(source_path, filename)

    @staticmethod
    def full_output_path(filename=None):
        dist_path = DATASET_DIR + 'dist\\'
        if not os.path.isdir(dist_path):
            os.mkdir(dist_path)

        if filename is None:
            return dist_path

        return os.path.join(dist_path, filename)

    @property
    def json_data(self):
        return [encode_document({'variable': v.name, 'data': self.data(v_name=v.name)}) for v in self.variables]

    def write_to_disk(self):

        dist_path = self.full_output_path('.'.join(self.name.split('.')[:-1]))

        # make sure the dataset folder exists
        if not os.path.isdir(dist_path):
            os.mkdir(dist_path)

        with open('%s\\dataset_info.json' % dist_path, 'w') as output:
            output.write(json.dumps(self.dataset.to_json()))

        with open('%s\\variables.json' % dist_path, 'w') as output:
            output.write(json.dumps([v.to_json() for v in self.variables]))

        with open('%s\\dimensions.json' % dist_path, 'w') as output:
            output.write(json.dumps([d.to_json() for d in self.dimensions]))

        # make sure the actual data folder exists
        if not os.path.isdir('%s\\data' % dist_path):
            os.mkdir('%s\\data' % dist_path)

        for datum in self.json_data:
            with open('%s\\data\\%s.json' % (dist_path, datum['variable']), 'w') as output:
                output.write(json.dumps(datum))

    def write_to_db(self, db):

        # insert dataset info
        dataset_id = db.datasets.insert_one(self.dataset.to_json()).inserted_id

        # add dimensions
        dimension_docs = []
        dimension_docs_by_name = {}
        for d in self.dimensions:
            dimension_doc = d.to_json()
            dimension_doc['dataset_id'] = dataset_id
            dimension_docs.append(dimension_doc)
            dimension_docs_by_name[dimension_doc['name']] = dimension_doc

        # bulk insert
        dimension_ids = db.dimensions.insert_many(dimension_docs).inserted_ids
        for idx, dimension_id in enumerate(dimension_ids):
            dimension_docs[idx]['_id'] = dimension_id

        # add variables
        variable_docs = []
        variable_docs_by_name = {}
        for v in self.variables:
            variable_doc = v.to_json()
            variable_doc['dataset_id'] = dataset_id

            # replace references to dimension names with dimension ObjectIDs
            dims = variable_doc['dimensions'][:]
            del variable_doc['dimensions']
            variable_doc['dimension_ids'] = []
            for dim in dims:
                variable_doc['dimension_ids'].append(dimension_docs_by_name[dim]['_id'])

            variable_docs.append(variable_doc)
            variable_docs_by_name[variable_doc['name']] = variable_doc

        # bulk insert
        variable_ids = db.variables.insert_many(variable_docs).inserted_ids
        for idx, variable_id in enumerate(variable_ids):
            variable_docs[idx]['_id'] = variable_id

        # add actual data
        data_docs = []
        for datum in self.json_data:
            # replace reference to variable name with variable ObjectIDs
            datum['variable_id'] = variable_docs_by_name[datum['variable']]['_id']
            del datum['variable']
            datum['dataset_id'] = dataset_id
            data_docs.append(datum)

        # bulk insert
        data_ids = db.data.insert_many(data_docs).inserted_ids
