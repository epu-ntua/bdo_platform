from random import random

import time
import xlrd
from fractions import gcd

from decimal import Decimal

from aggregator.converters.base import *


class ExcelFnkDataConverter(BaseConverter):
    _f = None
    _max_rows = None
    _sheet_data = None
    header_row = 3
    data_row = 5

    def __init__(self, name):
        self.name = name
        workbook = xlrd.open_workbook(BaseConverter.full_input_path(name))
        sheet = workbook.sheet_by_index(0)
        self.dataset_title = '.'.join(name.split('.')[:-1])

        # set up possible variables
        self.available_variables = {
            'average speed': {'unit': 'mph'},
            'average rpm': {'unit': 'rpm'},
        }

        # initially we don't know the position of the dimension name in the excel
        for v_name in self.available_variables.keys():
            self.available_variables[v_name]['idx'] = None

        # set up possible dimensions
        self.available_dimensions = {
            #'eosp date': {'unit': 'timestamp'},
            'latitude': {'unit': 'degree_north',
                         'transform': 'coordinates'},
            'lontitude': {'unit': 'degree_east',
                          'transform': 'coordinates'},
            'voyage no': {'unit': '', 'title': 'Voyage No'}
        }

        # initially we don't know the position of the dimension name in the excel
        for d_name in self.available_dimensions.keys():
            self.available_dimensions[d_name]['idx'] = None

        if sheet.cell_value(self.header_row, 0) != 'DATE':
            raise ValueError('Invalid excel format - can not be interpreted as FNK export')

        # load sheet data
        self._sheet_data = []
        row_idx = 0
        while True:
            row_data = []
            col_idx = 0
            while True:
                try:
                    row_data.append(sheet.cell_value(row_idx, col_idx))
                    col_idx += 1
                except IndexError:
                    break

            if not row_data:
                break
            self._sheet_data.append(row_data)
            row_idx += 1

        # cleanup
        # TODO cleanup

    def cell_value(self, r, c):
        return self._sheet_data[r][c]

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

                        try:
                            dimension.min = self.available_dimensions[d_name]['min']
                            dimension.max = self.available_dimensions[d_name]['max']
                            dimension.step = self.available_dimensions[d_name]['step']
                        except KeyError:
                            values = []
                            rdx = self.data_row
                            while True:
                                try:
                                    v = self.get_value_from_sheet(self.available_dimensions[d_name], rdx)
                                    if v is None or v == '':
                                        break

                                    values.append(self.normalize(dimension, v))
                                    rdx += 1
                                except IndexError:
                                    break

                            values.sort()

                            dimension.min = values[0]
                            dimension.max = values[-1]
                            dimension.step = denorm(reduce(gcd,
                                                    list(set(
                                                        [s for s in
                                                         [abs(norm(values[i + 1] - values[i])) for i in range(0, len(values) - 1)]
                                                         if gt_zero(s)]))), type(values[0]))
                            dimension.values = list(set(values))

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
        combinations = []
        rdx = self.data_row
        v = self.get_variable(v_name)
        while True:
            try:
                combination = []
                for d_name in v.dimensions:
                    combination.append((rdx - self.data_row,
                                        self.normalize(self.get_dimension(d_name),
                                                       self.get_value_from_sheet(self.available_dimensions[d_name], rdx))))

                combinations.append(combination)
                rdx += 1
            except IndexError:
                break

        return combinations

    def count(self, v_name):
        try:
            return len(self.variable_iter(v_name))
        except NotImplementedError:
            total_size = 1
            for d in self.dimensions:
                if d.values:
                    total_size *= len(d.values)
                else:
                    total_size *= int(((d.max - d.min)/d.step)) + 1

            return total_size

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
        if dimension.unit == 'timestamp' and type(value) in [str, unicode]:
            return time.mktime(datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').timetuple())

        return value
