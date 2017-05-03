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

        return document


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

        return document


class DatasetInfo(object):
    title = ''
    source = ''
    description = ''
    references = []

    def to_json(self):
        return {
            'title': self.title,
            'source': self.source,
            'description': self.description,
            'references': self.references,
        }


class DocumentEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(DocumentEncoder, self).default(obj)


class BaseConverter(object):
    name = None
    _document = None
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
    def full_input_path(filename):
        source_path = DATASET_DIR + 'source\\'
        if not os.path.isdir(source_path):
            os.mkdir(source_path)

        return os.path.join(DATASET_DIR + 'source\\', filename)

    @staticmethod
    def full_output_path(filename):
        dist_path = DATASET_DIR + 'dist\\'
        if not os.path.isdir(dist_path):
            os.mkdir(dist_path)

        return os.path.join(DATASET_DIR + 'dist\\', filename)

    @property
    def document(self):
        if self._document is None:
            self._document = {
                'dataset_info': self.dataset.to_json(),
                'dimensions': [d.to_json() for d in self.dimensions],
                'variables': [v.to_json() for v in self.variables],
                'data': [{'variable': v.name, 'data': self.data(v_name=v.name)} for v in self.variables],
            }

        return self._document

    def write_to_disk(self):

        dist_path = self.full_output_path('.'.join(self.name.split('.')[:-1]))

        # make sure the dataset folder exists
        if not os.path.isdir(dist_path):
            os.mkdir(dist_path)

        with open('%s\\dataset_info.json' % dist_path, 'w') as output:
            output.write(json.dumps(self.document['dataset_info'], cls=DocumentEncoder))

        with open('%s\\variables.json' % dist_path, 'w') as output:
            output.write(json.dumps(self.document['variables'], cls=DocumentEncoder))

        with open('%s\\dimensions.json' % dist_path, 'w') as output:
            output.write(json.dumps(self.document['dimensions'], cls=DocumentEncoder))

        # make sure the actual data folder exists
        if not os.path.isdir('%s\\data' % dist_path):
            os.mkdir('%s\\data' % dist_path)

        for datum in self.document['data']:
            with open('%s\\data\\%s.json' % (dist_path, datum['variable']), 'w') as output:
                output.write(json.dumps(datum, cls=DocumentEncoder))
