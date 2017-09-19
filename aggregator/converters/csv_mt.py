from random import random

import time
import xlrd
from fractions import gcd

from decimal import Decimal

from aggregator.converters.base import *


class CSVMarineTrafficConverter(BaseConverter):
    _f = None
    _max_rows = None
    _sheet_data = None
    header_row = 2
    data_row = 4

    def __init__(self, name):
        self.name = name
        self.csv_file = open(BaseConverter.full_input_path(name), 'r')
        self.dataset_title = '.'.join(name.split('.')[:-1])

        # set up possible variables
        self.available_variables = {
            'speed': {'unit': 'mph'},
            'course': {'unit': 'rpm'},
            'heading': {'unit': 'rpm'},
            # 'SHIP_ID': {'unit': 'rpm'},
        }

        # initially we don't know the position of the dimension name in the csv
        for v_name in self.available_variables.keys():
            self.available_variables[v_name]['idx'] = None

        # set up possible dimensions
        self.available_dimensions = {
            'lon': {'unit': 'degree_east'},
            'lat': {'unit': 'degree_north'},
            'ship_id': {'unit': 'mt_vessel_id', 'title': 'Ship ID'},
            'timestamp': {'unit': 'timestamp', }
        }

        # initially we don't know the position of the dimension name in the csv
        for d_name in self.available_dimensions.keys():
            self.available_dimensions[d_name]['idx'] = None

        # load cache
        self.cache = {
            'size': 1000,
        }
        self.load_data()

    def load_data(self, row_offset=0):
        if 'offset' in self.cache and self.cache['offset'] + self.cache['size'] == row_offset:
            cur_row = row_offset
        else:
            # go to file start
            self.csv_file.seek(0)
            cur_row = 0

            # ignore lines before
            while cur_row < row_offset:
                if not self.csv_file.readline():
                    raise IndexError
                cur_row += 1

        # read data
        _data = []
        while cur_row < row_offset + self.cache['size']:
            try:
                line = self.csv_file.readline()
                if not line:
                    break

                _data.append(line.replace('\n', '').split(';'))
            except:
                raise IndexError
            cur_row += 1

        # update cache
        self.cache['offset'] = row_offset
        self.cache['data'] = _data

    def cell_value(self, r, c):
        if not (self.cache['offset'] <= r < self.cache['offset'] + self.cache['size']):
            self.load_data(row_offset=(r / self.cache['size'])*self.cache['size'])

        v = self.cache['data'][r - self.cache['offset']][c]

        try:
            return int(v)
        except ValueError:
            try:
                return float(v)
            except ValueError:
                return v

    @property
    def dataset(self):
        if not self._dataset:
            self._dataset = DatasetInfo()
            self._dataset.title = self.dataset_title

        return self._dataset

    @property
    def dimensions(self):

        def gt_zero(x):
            if type(x) == datetime.timedelta:
                return x > datetime.timedelta()

            return x > 0

        def norm(x):
            if type(x) == datetime.timedelta:
                return x.total_seconds()

            return x

        def denorm(x, tp):
            if tp == datetime.datetime:
                return datetime.timedelta(seconds=x)

            return x

        if not self._dimensions:
            self._dimensions = []

            idx = 0
            while True:
                try:
                    d_name = self.cell_value(self.header_row, idx).lower()

                    d_name = d_name.replace('\n', ' ')

                    if d_name in self.available_dimensions.keys():

                        # store column for data reference
                        self.available_dimensions[d_name]['idx'] = idx

                        dimension = Dimension()
                        dimension.name = d_name

                        try:
                            dimension.title = self.available_dimensions[d_name]['title']
                        except KeyError:
                            dimension.title = d_name.replace(' ', '_').title()

                        dimension.unit = self.available_dimensions[d_name]['unit']

                        dimension.min = None
                        dimension.max = None
                        dimension.step = None

                        # add to dimensions
                        self._dimensions.append(dimension)
                except IndexError:
                    break

                idx += 1

        return self._dimensions

    @property
    def variables(self):
        if not self._variables:
            self._variables = []

            idx = 0
            while True:
                try:
                    v_name = self.cell_value(self.header_row, idx).lower()

                    v_name = v_name.replace('\n', ' ')

                    if v_name in self.available_variables.keys():
                        # store column for data reference
                        self.available_variables[v_name]['idx'] = idx

                        # rand var
                        variable = Variable()
                        variable.name = v_name
                        try:
                            variable.title = self.available_variables[v_name]['title']
                        except KeyError:
                            variable.title = v_name.replace('_', ' ').title()

                        try:
                            variable.unit = self.available_variables[v_name]['units']
                        except KeyError:
                            variable.unit = ''

                        variable.dimensions = [d.name for d in self.dimensions]

                        self._variables.append(variable)

                    idx += 1
                except IndexError:
                    break

        return self._variables

    def data(self, v_name):
        return None

    @property
    def max_rows(self):
        if self._max_rows is None:
            rdx = self.data_row
            while True:
                try:
                    self.cell_value(rdx, 0)
                    rdx += 1
                except IndexError:
                    break

            self._max_rows = rdx - self.data_row + 1

        return self._max_rows

    def variable_iter(self, v_name):
        rdx = self.data_row
        v = self.get_variable(v_name)
        while True:
            try:
                combinations = []
                for d_name in v.dimensions:
                    combinations.append((rdx,
                                         self.normalize(self.get_dimension(d_name), self.get_value_from_sheet(self.available_dimensions[d_name], rdx)),
                                         ))

                combinations.append(
                    (self.cell_value(rdx, self.available_variables[v.name]['idx']), 'V'))
                rdx += 1

                yield combinations
            except IndexError:
                break

    def count(self, v_name):
        return self.max_rows

    def get_value(self, v_name, comb):
        v = self.get_variable(v_name)
        rdx = self.data_row
        while True:
            try:
                for idx, combi in enumerate(comb):
                    if self.normalize(self.get_dimension(v.dimensions[idx]),
                                      self.get_value_from_sheet(self.available_dimensions[v.dimensions[idx]], rdx)) != combi[1]:
                        break
                else:
                    return self.get_value_from_sheet(self.available_variables[v_name], rdx)

                rdx += 1
            except IndexError:
                break

        return None

    def get_value_from_sheet(self, param, row_idx):
        v = self.cell_value(row_idx, param['idx'])
        if v is None or v == '':
            return v

        # special parse cases
        if 'transform' in param.keys():
            if param['transform'] == 'coordinates':
                v_next = self.cell_value(row_idx, param['idx'] + 1)
                v = Decimal('%d.%02d' % (v, v_next))

        return v

    def normalize(self, dimension, value):
        # time
        if dimension.unit == 'timestamp':
            return datetime.datetime.strptime(value[:-4], '%Y-%m-%d %H:%M:%S')

        return value
