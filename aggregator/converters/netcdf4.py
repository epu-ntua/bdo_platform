from netCDF4 import Dataset

from aggregator.converters.base import *


class NetCDF4Converter(BaseConverter):
    _f = None

    def __init__(self, name):
        self.name = name
        self._f = Dataset(BaseConverter.full_input_path(name), mode='r')

        # validations
        if not self._f.dimensions.keys():
            raise ValueError('No dimensions found')

        if self._f.variables.keys().__len__() <= self._f.dimensions.keys().__len__():
            raise ValueError('No variables found')

    @property
    def dataset(self):
        if not self._dataset:
            self._dataset = DatasetInfo()
            self._dataset.title = self._f.title
            self._dataset.source = self._f.institution
            self._dataset.references = [self._f.references]
            self._dataset.description = self._f.history

        return self._dataset

    def _parse_base_variable(self, target, source):
        target.unit = source.units
        target.title = source.long_name

    def _parse_variable(self, target, source):
        # variable extends base variable
        self._parse_base_variable(target, source)
        target.scale_factor = source.scale_factor
        target.add_offset = source.add_offset
        target.cell_methods = source.cell_methods.split(' ')
        target.type_of_analysis = source.type_of_analysis
        try:
            target.extra_info = {
                'WMO_code': source.WMO_code,
            }
        except AttributeError:
            pass

    def _parse_dimension(self, target, source, v_source):
        # dimension extends base variable
        self._parse_base_variable(target, v_source)

        v = self._f.variables[target.name]
        d_data = v[:]
        target.min = d_data[0]
        target.max = d_data[d_data.__len__() - 1]

        try:
            target.step = v.step
        except AttributeError:
            target.step = d_data[1] - d_data[0]

        try:
            target.axis = source.axis
        except AttributeError:
            pass

    @property
    def dimensions(self):
        if not self._dimensions:
            self._dimensions = []
            for d_name in self._f.dimensions.keys():

                _v = self._f.variables[d_name]
                _d = self._f.dimensions[d_name]
                dimension = Dimension()
                dimension.name = d_name
                self._parse_dimension(target=dimension, source=_d, v_source=_v)

                # add to dimensions
                self._dimensions.append(dimension)

        return self._dimensions

    @property
    def variables(self):
        if not self._variables:
            self._variables = []
            for v_name in self._f.variables.keys():

                # exclude dimensions
                if v_name in self._f.dimensions.keys():
                    continue

                _v = self._f.variables[v_name]
                variable = Variable()
                variable.name = v_name
                self._parse_variable(target=variable, source=_v)

                # reference dimensions
                variable.dimensions = []
                for d_name in _v._CoordinateAxes.strip().split(' '):
                    if not self.get_dimension(d_name):
                        raise ValueError('Dimension "%s" was not defined' % d_name)

                    variable.dimensions.append(d_name)

                # add to variables
                self._variables.append(variable)

        return self._variables

    def data(self, v_name):
        return self._f.variables[v_name][:]

