# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import decimal
import datetime
import copy
import time
from collections import OrderedDict
import re
import sympy
from threading import Thread

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models import *

from aggregator.models import *

from query_designer.formula_functions import *
from query_designer.query_processors.utils import SolrResultEncoder, PostgresResultEncoder


class Query(Model):
    user = ForeignKey(User, related_name='queries')
    title = TextField(default='Untitled query')
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)
    document = JSONField()
    design = JSONField(blank=True, null=True, default=None)
    count = IntegerField(blank=True, null=True, default=None)
    headers = JSONField(blank=True, null=True, default=None)

    def __unicode__(self):
        return '<#%d "%s"%s>' % (self.pk, self.title, ' (%d results)' % self.count if self.count is not None else '')

    @staticmethod
    def operator_to_str(op, mode='postgres'):
        return {
            # comparison
            'eq': ('=', ':'),
            'neq': ('!=', None),
            'gt': ('>', None),
            'gte': ('>=', None),
            'lt': ('<', None),
            'lte': ('<=', None),
            'mod': ('%', None),

            # boolean
            '&&': ('AND', 'AND'),
            'and': ('AND', 'AND'),
            '||': ('OR', 'OR'),
            'or': ('OR', 'OR'),
            '!': ('NOT', None),
            'not': ('NOT', None),
        }[op.lower()][0 if mode == 'postgres' else 1]

    def process_filters(self, filters, mode='postgres', quote=False):
        # end value
        if type(filters) in [int, float]:
            try:
                col_name = ''
                from_order = int(filters[filters.find('i')+1:filters.find('_')])
                if from_order >= 0:
                    table_name = self.document['from'][from_order]['name']
                    for x in self.document['from'][from_order]['select']:
                        if x['name'] == filters:
                            if x['type'] != 'VALUE':
                                col_name = Dimension.objects.get(pk=x['type']).data_column_name
                            else:
                                col_name = 'value'
                    filters = table_name + '.' + col_name
            except:
                return filters
            return filters

        if type(filters) in [str, unicode]:
            if quote and (mode == 'solr') and filters.strip() != '*' and (not filters.startswith('"')) and filters:
                return '"%s"' % filters
            else:
                try:
                    col_name = ''
                    from_order = int(filters[filters.find('i') + 1:filters.find('_')])
                    if from_order >= 0:
                        table_name = self.document['from'][from_order]['name']
                        for x in self.document['from'][from_order]['select']:
                            if x['name'] == filters:
                                if x['type'] != 'VALUE':
                                    col_name = Dimension.objects.get(pk=x['type']).data_column_name
                                else:
                                    col_name = 'value'
                        filters = table_name + '.' + col_name
                except:
                    return filters
                return filters

        # Special case: parsing location filters
        # inside_rect|outside_rect <<lat_south,lng_west>,<lat_north,lng_east>>

        if filters['op'] in ['inside_rect', 'outside_rect', ]:
            rect_start = filters['b'].split('<')[2].split('>,')[0].split(',')
            rect_end = filters['b'].split('>,<')[1].split('>')[0].split(',')

            #lat = filters['a'] + '_latitude'
            #lng = filters['a'] + '_longitude'

            lat_col_name = ''
            lon_col_name = ''
            from_order = int(filters['a'][1])
            table_name = self.document['from'][from_order]['name']
            for x in self.document['from'][from_order]['select']:
                if x['name'] == (filters['a'] + '_latitude'):
                    lat_col_name = Dimension.objects.get(pk=x['type']).data_column_name
                if x['name'] == (filters['a'] + '_longitude'):
                    lon_col_name = Dimension.objects.get(pk=x['type']).data_column_name

            lat = table_name+'.'+lat_col_name
            lng = table_name+'.'+lon_col_name

            result = '%s >= %s AND %s <= %s' % (lat, rect_start[0], lat, rect_end[0])
            result += ' AND %s >= %s AND %s <= %s' % (lng, rect_start[1], lng, rect_end[1])
            #lat = filters['a'] + '_latitude'
            #lng = filters['a'] + '_longitude'

            if mode == 'solr':
                result = '%s:[%s TO %s]' % (lat, rect_start[0], rect_end[0])
                result += ' AND %s:[%s TO %s]' % (lng, rect_start[1], rect_end[1])
            else:
                result = '%s >= %s AND %s <= %s' % (lat, rect_start[0], lat, rect_end[0])
                result += ' AND %s >= %s AND %s <= %s' % (lng, rect_start[1], lng, rect_end[1])

            if filters['op'] == 'outside_rect':
                if mode == 'postgres':
                    result = 'NOT(%s)' % result
                else:
                    result = '-(%s)' % result

            return result

        result = ''
        _op = filters['op'].lower()
        if mode == 'solr' and _op in ['neq', 'gt', 'gte', 'lt', 'lte', 'mod', '!', 'not']:
            if _op == 'neq':
                result = '-%s:%s' % (self.process_filters(filters['a']), self.process_filters(filters['b']))
            elif _op in ['gt', 'gte']:
                result = '%s:[%s TO *]' % (self.process_filters(filters['a']), self.process_filters(filters['b']))
            elif _op in ['lt', 'lte']:
                result = '%s:[* TO %s]' % (self.process_filters(filters['a']), self.process_filters(filters['b']))
            elif _op == 'mod':
                result = 'mod(%s, %s)' % (self.process_filters(filters['a']), self.process_filters(filters['b']))
            elif _op in ['!', 'not']:
                raise NotImplementedError('TODO fix missing NOT operator in solr')

        else:
            _a = self.process_filters(filters['a'], mode=mode)
            _b = self.process_filters(filters['b'], mode=mode, quote=True)

            result = '%s %s %s' % \
                   (('(%s)' % _a) if type(_a) not in [str, unicode, int, float] else _a,
                    Query.operator_to_str(filters['op'], mode=mode),
                    ('(%s)' % _b) if type(_b) not in [str, unicode, int, float] else _b)

        return result

    @staticmethod
    def threaded_fetchall(conn, query, count):

        def fetch_data_page(results, offset=0, limit=100):
            cur = conn.cursor()
            cur.execute(query + ' OFFSET %d LIMIT %d' % (offset, limit))
            results.extend(cur.fetchall())

        # try threaded fetch
        unlimited_results_page_size = 50000
        workers = 5
        current_offset = 0
        all_rows = []

        while current_offset <= count:
            print current_offset
            threads = []
            for w in range(0, workers):
                if current_offset + w * unlimited_results_page_size > count:
                    break

                thread = Thread(target=fetch_data_page,
                                args=(all_rows,
                                      current_offset + w * unlimited_results_page_size,
                                      unlimited_results_page_size))
                thread.start()
                threads.append(thread)

            # wait for all to finish
            for k, thread in enumerate(threads):
                print 'waiting %d' % (k+1)
                thread.join()

            current_offset += unlimited_results_page_size * workers

        return all_rows

    def process(self, dimension_values='', variable='', only_headers=False, commit=True, execute=False, raw_query=False):
        if 'POSTGRES' in Variable.objects.get(pk=self.document['from'][0]['type']).dataset.stored_at:
            from query_designer.query_processors.postgres import process as q_process
            encoder = PostgresResultEncoder
        else:
            from query_designer.query_processors.solr import process as q_process
            encoder = SolrResultEncoder

        data = q_process(self, dimension_values=dimension_values, variable=variable,
                         only_headers=only_headers, commit=commit,
                         execute=execute, raw_query=raw_query)

        return data, encoder

    def execute(self, dimension_values='', variable='', only_headers=False, commit=True):
        return self.process(dimension_values, variable, only_headers, commit, execute=True)

    @property
    def raw_query(self):
        # remove several keys from query
        doc = copy.deepcopy(self.document)
        for key in ['limit', 'offset', 'granularity']:
            if key in self.document:
                del self.document[key]

        # get raw query
        res = self.process(dimension_values='', variable='', only_headers=True, commit=False,
                           execute=False, raw_query=True)

        # restore initial doc
        self.document = doc

        return res[0]['raw_query']


class InvalidUnitError(ValueError):
    pass


class Formula(Model):
    # generic information
    date_created = DateTimeField(auto_now_add=True)
    date_updated = DateTimeField(auto_now=True)
    created_by = ForeignKey(User, blank=True, null=True, default=None)
    name = TextField(blank=False, null=False)

    # the actual formula
    # e.g (`energydemandbefore_19` - `energydemandafter_20`)/`energydemandbefore_19`
    value = TextField(blank=False, null=False)

    # is this a public formula?
    is_valid = BooleanField(default=False)
    is_public = BooleanField(default=False)

    @property
    def dependencies(self):
        """
        :return: A list with all the variables used in the formula
        """
        return list(set([prop[1:-1] for prop in re.findall(r'`\w+`', self.value)]))

    @property
    def internal_value(self):
        return '$%d' % self.pk

    @staticmethod
    def math():
        return [fn['name'].split('(')[0] for fn in MATH_FUNCTIONS]

    @staticmethod
    def random():
        return [fn['name'].split('(')[0] for fn in RAND_FUNCTIONS]

    @staticmethod
    def trig():
        return [fn['name'].split('(')[0] for fn in TRIG_FUNCTIONS]

    @staticmethod
    def safe_function_info():
        result = []

        for item in MATH_FUNCTIONS:
            result.append((item['name'], item['description']))

        for item in RAND_FUNCTIONS:
            result.append((item['name'], item['description']))

        for item in TRIG_FUNCTIONS:
            result.append((item['name'], item['description']))

        return result

    @staticmethod
    def functions():
        return [fn[0].split('(')[0] for fn in Formula.safe_function_info()]

    @staticmethod
    def safe(value):
        """
        :param value: A potential formula
        :return: True if formula contains only numbers, operators and safe functions, False otherwise
        """
        for token in re.findall(r"[\w']+", value):
            try:
                float(token)
            except ValueError:
                # allowed functions here
                if token not in Formula.functions():
                    return False

            return True

    @staticmethod
    def find_unit(variable):
        try:
            return Variable.objects.filter(name=variable)[0].unit
        except IndexError:
            return Dimension.objects.filter(name=variable)[0].unit

    @staticmethod
    def _normalize_unit(unit):
        """
        :param unit: The continuous version of the unit, e.g "€/kWh"
        :return:
        """
        unit_str = unit
        unit_str = unit_str.replace('kWh', 'kW*h').replace('²', '**2')

        return unit_str, re.split(r'[\s,.|/*]+', unit_str)

    @property
    def unit(self):
        try:
            return self.suggest_unit(fail_on_invalid=False)
        except ValueError:
            return '-'

    def suggest_unit(self, fail_on_invalid=True):

        # ignore minus as it could incorrectly cause expressions to collapse
        # e.g € - € => €, not empty unit
        value = self.value.replace('-', '+').replace(' ', '')
        units = {}

        # this is the symbols variable, should not use any unit character inside
        q = []

        # make sure value is safe to proceed
        if self.errors(include_unit_errors=False):
            raise ValueError('Can\'t detect unit of invalid expression')

        # replace each dependency with its unit & define symbols
        unit_cnt = 0
        for dependency in self.dependencies:
            unit_str, du = Formula._normalize_unit(Formula.find_unit(dependency))
            if not du:
                value = value.replace('`' + dependency + '`', '1')

            for unit in du:
                try:
                    # do not replace numbers with tokens
                    float(unit)
                except ValueError:
                    if unit not in units:
                        units[unit] = 'q[%d]' % unit_cnt
                        q.append(sympy.Symbol(unit))
                        unit_cnt += 1

                    unit_str = unit_str.replace(unit, units[unit])

            # replace in value
            value = value.replace('`' + dependency + '`', '(' + unit_str + ')')

        # remove functions
        for fn in Formula.functions():
            value = value.replace(str(fn) + '(', '(')

        # simplify expression
        expr_result = str(eval(value))

        # replace original symbols
        for unit in units:
            expr_result = expr_result.replace(units[unit], unit)

        # replace ** with ^
        expr_result = expr_result.replace('**', '^')

        # remove digits
        result = ''
        to_remove_constant = True
        for x in expr_result:
            if x == ' ':
                continue

            try:
                int(x)

                if not to_remove_constant:
                    result += x
            except ValueError:
                result += x

            # should not remove the next constant if it exposes to power
            to_remove_constant = x not in ['^', ]

        # no unit remaining -- assume percentage:
        if not result:
            return '%'

        # remove trailing symbols
        while result and result[0] in ['+', '*', ]:
            result = result[1:]

        while result and result[len(result) - 1] in ['+', '*', '/']:
            result = result[:-1]

        # if addition is included, the formula most probably does not make sense
        if '+' in result and fail_on_invalid:
            # format error string
            adders = result.split('+')
            err_str = adders[0]
            for idx, term in enumerate(adders[1:]):
                if not term.strip():
                    continue

                if idx == 0:
                    err_str += ' with %s' % term
                elif idx + 2 < len(adders):
                    err_str += ', %s' % term
                else:
                    err_str += ' and %s' % term

            # raise error
            raise InvalidUnitError('Formula seems to be incorrect: adding %s' % err_str)

        if len(result):
            if result[0] == '*':
                result = result[1:]
            elif result[0] == '/':
                result = '1' + result[1:]

        return result

    def apply(self, context):
        """
        :param context: A dictionary of variables and their values
        :return: The result of the formula after applying the context
        """
        # modules for formula calculation
        ###

        # make sure all values are there
        for dependency in self.dependencies:
            if dependency not in context:
                raise ValueError('Missing value "%s"' % dependency)

        # apply context
        value = self.value
        for key in context:
            value = value.replace('`' + key + '`', str(context[key]))

        # make sure user input is safe
        if not Formula.safe(value):
            raise ValueError('Unsafe formula "%s"' % value)

        # remove functions
        for fn in Formula.functions():
            value = value.replace(str(fn) + '(', '(')

        # evaluate the expression
        try:
            result = eval(value)
        except ZeroDivisionError:
            result = None

        # respond
        return result

    def errors(self, include_unit_errors=True):
        """
        :return: A list of all the errors in the formula
        """
        dummy_context = {}
        errors = []
        for prop in self.dependencies:
            # make sure the variable is valid
            if prop not in [v.name for v in Variable.objects.all()] + [d.name for d in Dimension.objects.all()]:
                errors.append('Unknown variable %s' % prop)

            dummy_context[prop] = 0

        try:
            dummy_result = self.apply(dummy_context)
            if type(dummy_result) not in [int, float, type(None)]:
                errors.append('Incorrect return type %s: Must be either an int or a float' % type(dummy_result))
                return errors
        except SyntaxError as se:
            try:
                errors.append(str(se).split(' (')[0])
            except IndexError:
                errors.append(str(se))
        except ValueError:
            errors.append('Unknown expression')

        if include_unit_errors and not errors:
            try:
                self.suggest_unit()
            except InvalidUnitError as err:
                errors.append(str(err))

        return errors

    def save(self, *args, **kwargs):
        """
        Override the save method to store the `valid`
        """
        try:
            self.is_valid = len(self.errors(include_unit_errors=False)) == 0
        except ValueError:  # unsafe formula or incorrect context
            self.is_valid = False

        super(Formula, self).save(*args, **kwargs)

    def __str__(self):
        return '=%s' % self.value
