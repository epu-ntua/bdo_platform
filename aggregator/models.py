from django.contrib.postgres.fields import ArrayField
from django.db.models import *
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.db import connection

import math

from netCDF4._netCDF4 import num2date


class Dataset(Model):
    title = TextField()
    source = TextField()
    description = TextField()
    references = ArrayField(TextField())

    class Meta:
        ordering = ['-id']

    def to_json(self):
        return {
            '_id': str(self.pk),
            'title': self.title,
            'source': self.source,
            'description': self.description,
            'references': self.references,
        }

    def __unicode__(self):
        return self.title


class BaseVariable(Model):
    name = CharField(max_length=256)
    title = CharField(max_length=256)
    unit = CharField(max_length=256)

    class Meta:
        abstract = True


class Dimension(BaseVariable):
    variable = ForeignKey('Variable', related_name='dimensions')

    data_column_name = CharField(max_length=255)
    min = DecimalField(blank=True, null=True, default=None, max_digits=100, decimal_places=50)
    max = DecimalField(blank=True, null=True, default=None, max_digits=100, decimal_places=50)
    step = DecimalField(blank=True, null=True, default=None, max_digits=100, decimal_places=50)
    axis = TextField(blank=True, null=True, default=None)

    class Meta:
        ordering = ['pk']

    def __unicode__(self):
        return u'%s' % self.title

    def to_json(self):
        return {
            '_id': str(self.pk),
            'name': self.name,
            'title': self.title,
            'unit': self.unit,
            'min': self.min,
            'max': self.max,
            'step': self.step,
            'axis': self.axis,
        }

    @property
    def data_column_name(self):
        return slugify(self.name, allow_unicode=False).replace('-', '_') + ('_%d' % self.pk)

    @property
    def sql_type(self):
        type_mapping = {}

        if self.unit.startswith('days since ') or \
                self.unit.startswith('hours since ') or \
                self.unit.startswith('minutes since ') or \
                self.unit.startswith('seconds since ') or \
                self.unit.startswith('milliseconds since '):
            return 'TIMESTAMP'

        try:
            return type_mapping[self.name]
        except KeyError:
            return 'numeric'

    def get_values_from_db(self):
        q_col_values = 'SELECT DISTINCT(%s) FROM %s ORDER BY %s' % \
                       (self.data_column_name, self.variable.data_table_name, self.data_column_name)

        cursor = connection.cursor()
        cursor.execute(q_col_values)
        values = []
        for row in cursor.fetchall():
            v = row[0]
            if (self.sql_type == 'numeric' or self.sql_type.startswith('numeric(')) and type(v) in [str, unicode]:
                values.append(float(v))
            else:
                values.append(v)

        return values

    def normalize(self, value):
        if self.unit and \
                (self.unit.startswith('days since ') or
                     self.unit.startswith('hours since ') or
                     self.unit.startswith('minutes since ') or
                     self.unit.startswith('seconds since ') or
                     self.unit.startswith('milliseconds since ')
                 ):
            return num2date(value, units=self.unit, calendar=u'gregorian')

        return value

    @property
    def values(self):
        if self.min is None or self.max is None or self.step is None:
            return self.get_values_from_db()

        result = []
        v = self.min
        while v <= self.max:
            result.append(self.normalize(v))
            v += self.step

        return result


class Variable(BaseVariable):
    dataset = ForeignKey('Dataset', related_name='variables')

    scale_factor = FloatField(default=1)
    add_offset = FloatField(default=0)
    cell_methods = ArrayField(TextField())
    type_of_analysis = TextField(blank=True, null=True, default=None)

    def __unicode__(self):
        return u'%s' % self.title

    def to_json(self):
        return {
            '_id': str(self.pk),
            'name': self.name,
            'title': self.title,
            'unit': self.unit,
            'scale_factor': self.scale_factor,
            'add_offset': self.add_offset,
            'cell_methods': self.cell_methods,
            'type_of_analysis': self.type_of_analysis,
        }

    @property
    def data_table_name(self):
        return slugify(self.name, allow_unicode=False).replace('-', '_') + ('_%d' % self.pk)

    def create_data_table(self, cursor, with_indices=True):
        # gather columns
        columns = []
        for d in self.dimensions.all():
            columns.append('%s %s' % (d.data_column_name, d.sql_type))
        columns.append('value double precision')

        # create table
        cursor.execute('CREATE TABLE %s (%s);' %
                       (self.data_table_name, ','.join(columns)))

        if with_indices:
            self.create_indices(cursor=cursor)

    def create_indices(self, cursor):
        # add indices
        for d in self.dimensions.all():
            cursor.execute('CREATE INDEX idx_%d_%s ON %s (%s);' %
                           (self.pk, d.data_column_name, self.data_table_name, d.data_column_name))

    def delete_data_table(self, cursor):
        # delete indeces
        for d in self.dimensions.all():
            cursor.execute('DROP INDEX IF EXISTS idx_%d_%s;' % (self.pk, d.data_column_name))

        # delete table
        cursor.execute('DROP TABLE IF EXISTS %s;' % self.data_table_name)

    def count_values(self, cursor):
        cursor.execute('SELECT COUNT (*) FROM %s;' % self.data_table_name)
        return cursor.fetchone()[0]


# on variable delete, cleanup
@receiver(pre_delete, sender=Variable)
def log_deleted_question(sender, instance, **kwargs):
    instance.delete_data_table(cursor=connection.cursor())
