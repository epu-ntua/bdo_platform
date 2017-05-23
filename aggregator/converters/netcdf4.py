from netCDF4 import Dataset, num2date

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
            try:
                self._dataset.title = self._f.title
            except AttributeError:
                self._dataset.title = '.'.join(self.name.split('.')[:-1])

            try:
                self._dataset.source = self._f.institution
            except AttributeError:
                self._dataset.source = 'Unknown'

            try:
                self._dataset.references = [self._f.references]
            except AttributeError:
                self._dataset.references = []

            try:
                self._dataset.description = self._f.history
            except AttributeError:
                self._dataset.description = ''

        return self._dataset

    def _parse_base_variable(self, target, source):
        try:
            target.unit = source.units.lower()
        except AttributeError:
            target.unit = ''

        try:
            target.title = source.long_name
        except AttributeError:
            target.title = source.name

    def _parse_variable(self, target, source):
        # variable extends base variable
        self._parse_base_variable(target, source)
        try:
            target.scale_factor = source.scale_factor
        except AttributeError:
            pass

        try:
            target.add_offset = source.add_offset
        except AttributeError:
            pass

        try:
            target.cell_methods = source.cell_methods.split(' ')
        except AttributeError:
            pass

        try:
            target.type_of_analysis = source.type_of_analysis
        except AttributeError:
            pass

        try:
            target.extra_info = {
                'WMO_code': source.WMO_code,
            }
        except AttributeError:
            pass

    def _parse_dimension(self, target, source, v_source=None):
        # dimension extends base variable
        if not v_source:
            target.title = source.name
            target.unit = ''
        else:
            self._parse_base_variable(target, v_source)

        try:
            v = self._f.variables[target.name]
            d_data = v[:]
            target.min = d_data[0]
            target.max = d_data[d_data.__len__() - 1]

            try:
                target.step = v.step
            except AttributeError:
                try:
                    target.step = d_data[1] - d_data[0]
                except IndexError:
                    target.step = None
        except KeyError:
            try:
                default_v = [self._f.variables[v] for v in self._f.variables
                             if target.name in self._f.variables[v].dimensions][0]
            except IndexError:
                raise ValueError('Could not parse dimension %s' % target.name)

            # no dimension information, best guess
            target.min = 1
            target.step = 1
            d_data = default_v[:]
            for d in default_v.dimensions:
                if d == target.name:
                    target.max = len(d_data)
                    break

                d_data = d_data[0]

        try:
            target.axis = source.axis
        except AttributeError:
            pass

    @property
    def dimensions(self):
        if not self._dimensions:
            self._dimensions = []
            for d_name in self._f.dimensions.keys():
                try:
                    _v = self._f.variables[d_name]
                except KeyError:
                    _v = None

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
                for d_name in _v.dimensions:
                    if d_name not in variable.dimensions:
                        if not self.get_dimension(d_name):
                            raise ValueError('Dimension "%s" was not defined' % d_name)

                        variable.dimensions.append(d_name)

                # add to variables
                self._variables.append(variable)

        return self._variables

    def data(self, v_name):
        return self._f.variables[v_name][:]

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

