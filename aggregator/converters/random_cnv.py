from random import random

from netCDF4 import Dataset, num2date

from aggregator.converters.base import *


class RandomDataConverter(BaseConverter):
    _f = None

    def __init__(self, dimensions, title='Random dataset'):
        self.dataset_title = title
        self.dimension_config = dimensions

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
            for d_name in self.dimension_config.keys():
                d = self.dimension_config[d_name]
                dimension = Dimension()
                dimension.name = d_name
                dimension.title = d_name.replace(' ', '_').title()
                dimension.unit = d.get('unit', '')
                dimension.min = d.get('min', 0)
                dimension.max = d.get('max', 99)
                dimension.step = d.get('step', 1)

                # add to dimensions
                self._dimensions.append(dimension)

        return self._dimensions

    @property
    def variables(self):
        if not self._variables:
            # rand var
            variable = Variable()
            variable.name = 'rnd'
            variable.title = 'Random variable'
            variable.unit = 'rands'
            variable.dimensions = [d.name for d in self.dimensions]

            # add as variable
            self._variables = [variable]

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
        if dimension.unit and \
                (dimension.unit.startswith('days since ') or
                 dimension.unit.startswith('hours since ') or
                 dimension.unit.startswith('minutes since ') or
                 dimension.unit.startswith('seconds since ') or
                 dimension.unit.startswith('milliseconds since ')
                 ):
            try:
                t_cal = dimension.calendar
            except AttributeError:
                try:
                    t_cal = self._f.variables[dimension.name].calendar
                except AttributeError:
                    t_cal = u'gregorian'

                setattr(dimension, 'calendar', t_cal)

            value = num2date(value, units=dimension.unit, calendar=t_cal)

        return value

