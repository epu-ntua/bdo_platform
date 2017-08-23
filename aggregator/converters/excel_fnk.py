from random import random

import xlrd

from aggregator.converters.base import *


class ExcelFnkDataConverter(BaseConverter):
    _f = None
    header_row = 3

    def __init__(self, name):
        self.name = name
        self.sheet = xlrd.open_workbook(BaseConverter.full_input_path(name)).sheet_by_index(0)
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
            'eosp date': {'unit': 'timestamp'},
            'latitude': {'unit': 'degree_north', 'step': 0.01, 'min': -90, 'max': 90},
            'lontitude': {'unit': 'degree_east', 'step': 0.01, 'min': -180, 'max': 180},
            'voyage no': {'unit': '', 'title': 'Voyage No'}
        }

        # initially we don't know the position of the dimension name in the excel
        for d_name in self.available_dimensions.keys():
            self.available_dimensions[d_name]['idx'] = None

        if self.sheet.cell_value(self.header_row, 0) != 'DATE':
            raise ValueError('Invalid excel format - can not be interpreted as FNK export')

    @property
    def dataset(self):
        if not self._dataset:
            self._dataset = DatasetInfo()
            self._dataset.title = self.dataset_title

        return self._dataset

    @property
    def dimensions(self):
        if not self._dimensions:
            self._dimensions = []

            idx = 0
            while True:
                d_name = self.sheet.cell_value(self.header_row, idx).lower()

                if not d_name:
                    break

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
                        rdx = self.header_row + 1
                        while True:
                            v = self.sheet.cell_value(rdx, idx)
                            if v is None or v == '':
                                break

                            values.append(self.normalize(dimension, v))

                        values.sort()
                        dimension.min = values[0]
                        dimension.max = values[-1]
                        dimension.step = min([values[i + 1] - values[i] for i in range(0, len(values) - 1)])

                    # add to dimensions
                    self._dimensions.append(dimension)

                idx += 1

        return self._dimensions

    @property
    def variables(self):
        if not self._variables:
            self._variables = []

            idx = 0
            while True:
                v_name = self.sheet.cell_value(self.header_row, idx).lower()

                if not v_name:
                    break

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

        return self._variables

    def data(self, v_name):
        return None

    def count(self, v_name):
        total_size = 1
        for d in self.dimensions:
            total_size *= int(((d.max - d.min)/d.step)) + 1

        return total_size

    def get_value(self, v_name, comb):
        return round(random(), 4)

    def normalize(self, dimension, value):
        # time
        if dimension.unit == 'timestamp':
            return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

        return value
