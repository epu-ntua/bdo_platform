import json
import os

import decimal
import bson
import itertools

import datetime
import numpy
from numpy.ma import MaskedArray

from bdo_platform.settings import DATASET_DIR
from aggregator.models import Dataset as AgDataset, Variable as AgVariable, Dimension as AgDimension


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
    MAX_DOCUMENT_SIZE = 16000000 # 16M limit on BSON documents
    AVERAGE_ELEMENT_SIZE = 16

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
        source_path = os.path.join(DATASET_DIR, 'source')
        if not os.path.isdir(source_path):
            os.mkdir(source_path)

        if filename is None:
            return source_path

        return os.path.join(source_path, filename)

    @staticmethod
    def full_output_path(filename=None):
        dist_path = os.path.join(DATASET_DIR, 'dist')
        if not os.path.isdir(dist_path):
            os.mkdir(dist_path)

        if filename is None:
            return dist_path

        return os.path.join(dist_path, filename)

    def predicted_document_size(self, dimension_sizes, shards):
        # predicted size if no shards
        full_document_size = reduce(lambda x, y: x*y, dimension_sizes) * self.AVERAGE_ELEMENT_SIZE

        # divide based on shards
        document_size = full_document_size
        for shard in shards:
            if shard:
                document_size /= (len(shard) + 0.0)

        return int(document_size)

    def get_document_shards(self, dimension_sizes):
        # predict document size
        # initially plan for no sharding
        shards = [[(0, dimension_sizes[idx])] for idx in xrange(dimension_sizes.__len__())]
        shard_idx = 0

        while self.predicted_document_size(dimension_sizes, shards) >= self.MAX_DOCUMENT_SIZE:

            # check if dimension can even be sharded
            if dimension_sizes[shard_idx] == 1 or \
                    ((type(shards[shard_idx]) == list) and len(shards[shard_idx]) == dimension_sizes[shard_idx]):
                shard_idx += 1
                continue

            # increase sharding on this dimension
            n_of_shards = len(shards[shard_idx]) + 1
            shard_size = dimension_sizes[shard_idx] / (n_of_shards + 0.0)
            shards[shard_idx] = [(int(idx * shard_size), int((idx + 1) * shard_size))
                                 for idx in xrange(n_of_shards)]

        return shards

    def json_documents(self, variable):
        print variable.name
        data = self.data(v_name=variable.name)

        dim_lens = []
        dt = data
        while True:
            if type(dt) not in [list, MaskedArray]:
                break

            dim_lens.append(dt.__len__())
            dt = dt[0]

        print dim_lens

        shards = self.get_document_shards(dim_lens)

        for shard in itertools.product(*shards):
            # slices
            slc = [slice(None)] * dim_lens.__len__()
            for idx, s in enumerate(shard):
                slc[idx] = slice(s[0], s[1])

            encoded_document = encode_document({
                'variable': variable.name,
                'offsets': [s[0] for s in shard],
                'values': data[slc]
            })
            yield encoded_document

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

        for variable in self.variables:
            with open('%s\\data\\%s.json' % (dist_path, variable.name), 'w') as output:
                for datum in self.json_documents(variable=variable):
                    output.write(json.dumps(datum))

    def store(self, target, stdout=None):
        """
        :param target: Either {'type': 'postgres', 'cursor': <Cursor>, 'withIndices': True|False} or
                              {'type': 'mongo', 'db': <MongoClient>}
        :param stdout: Optional output stream
        :return: Inserts data to database
        """

        def insert(iv):
            if target['type'] == 'postgres':
                target['cursor'].execute('INSERT INTO %s VALUES %s;' % (agv.data_table_name, ','.join(iv)))
            elif target['type'] == 'mongo':
                target['db'][v.name].insert_many(iv)

        def db_serialize(val):
            if type(val) == datetime.datetime:
                return "TIMESTAMP '%s'" % val.isoformat().replace('T', ' ')
            else:
                return str(val)

        if 'type' not in target:
            raise ValueError('Target type is required')

        if target['type'] not in ['postgres', 'mongo']:
            raise ValueError('Unsupported store target type')

        agd = None

        try:
            if target['type'] == 'postgres':
                # add datasets, variables & their dimensions
                agd = AgDataset.objects.create(title=self.dataset.title, source=self.dataset.source,
                                               description=self.dataset.description, references=self.dataset.references)
            elif target['type'] == 'mongo':
                agd = target['db'].datasets.insert(self.dataset.to_json())

            for v in self.variables:
                print v.name
                if target['type'] == 'postgres':
                    agv = AgVariable.objects.create(name=v.name, title=v.title, unit=v.unit,
                                                    scale_factor=v.scale_factor, add_offset=v.add_offset,
                                                    cell_methods=v.cell_methods, type_of_analysis=v.type_of_analysis,
                                                    dataset=agd)
                elif target['type'] == 'mongo':
                    v_doc = v.to_json()
                    v_doc['dataset_id'] = agd['_id']
                    agv = target['db'].variables.insert(v_doc)

                dimensions = []
                for dimension_name in v.dimensions:
                    for d in self.dimensions:
                        if d.name == dimension_name:
                            if target['type'] == 'postgres':
                                agdim = AgDimension.objects.create(name=d.name, title=d.title, unit=d.unit,
                                                                   min=decimal.Decimal(str(d.min)),
                                                                   max=decimal.Decimal(str(d.max)),
                                                                   step=decimal.Decimal(str(d.step))
                                                                   if d.step is not None else None,
                                                                   axis=d.axis,
                                                                   variable=agv)
                            elif target['type'] == 'mongo':
                                d_doc = d.to_json()
                                d_doc['variable_id'] = agv['_id']
                                agdim = target['db'].dimensions.insert(d_doc)

                            dimensions.append(agdim)
                            break

                # create data table for variable
                if target['type'] == 'postgres':
                    agv.create_data_table(cursor=target['cursor'], with_indices=target['with_indices'])

                # add data
                data = self.data(v_name=v.name)
                dim_values = []
                for dimension in dimensions:
                    vv = []
                    v = dimension.min
                    idx = 0
                    while v <= dimension.max:
                        vv.append((idx, self.normalize(dimension, v)))
                        if dimension.step is None:
                            break
                        idx += 1
                        v += dimension.step
                    dim_values.append(vv)

                insert_values = []
                progress = 0
                total = 1.0
                dt = data
                while True:
                    try:
                        total *= len(dt)
                        dt = dt[0]
                    except:
                        break

                for comb in itertools.product(*dim_values):
                    dt = data
                    error = False
                    for idx, dimension in enumerate(comb):
                        try:
                            dt = dt[comb[idx][0]]
                        except:
                            error = True
                            break

                    progress += 1
                    if error:
                        continue
                    if str(dt) != '--':
                        if target['type'] == 'postgres':
                            insert_values.append('(%s)' % ','.join([db_serialize(combi[1]) for combi in comb] + [str(dt)]))
                        elif target['type'] == 'mongo':
                            val_doc = {}
                            for idx, combi in comb:
                                val_doc[self.dimensions[idx].name] = combi[1]

                            val_doc['value'] = dt
                            insert_values.append(val_doc)
                    if len(insert_values) == 1000:
                        if stdout:
                            stdout.write("\r Adding data... %d%%" % (progress * 100 / total), ending='')
                            stdout.flush()

                        insert(insert_values)
                        insert_values = []

                if insert_values:
                    insert(insert_values)
                    insert_values = []

                if stdout:
                    stdout.write("\r Completed\t\t\t", ending='\n')
                    stdout.flush()
        except:
            if agd:
                agd.delete()

            raise
