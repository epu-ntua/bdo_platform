from django.contrib.postgres.fields import ArrayField
from django.db.models import *
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.db import connection
from django.db import models

import math

from netCDF4._netCDF4 import num2date
from django.contrib.postgres.fields import JSONField
from datetime import datetime

ACCESS_REQUEST_STATUS_CHOICES = (('open', 'open'),
                                 ('accepted', 'accepted'),
                                 ('rejected', 'rejected'))

DATASET_STORAGES = (
    ('LOCAL_POSTGRES', 'Local PostgreSQL instance'),
    ('UBITECH_POSTGRES', 'UBITECH\'s PostgreSQL instance at http://212.101.173.21'),
    ('UBITECH_PRESTO', 'UBITECH\'s PRESTO instance'),
    ('UBITECH_SOLR', 'Solr instance at http://212.101.173.50:8983'),
)

class Organization(Model):
    title = TextField()
    description = TextField()

    def __unicode__(self):
        return u'%s' % self.title


class Dataset(Model):
    title = TextField()
    source = TextField()
    description = TextField()
    order = IntegerField(default=999)
    references = ArrayField(TextField(), null=True)
    stored_at = CharField(max_length=32, choices=DATASET_STORAGES, default='LOCAL_POSTGRES')
    table_name = CharField(max_length=200)
    private = BooleanField(default=False)
    spatialEast = CharField(max_length=200, null=True)
    spatialSouth = CharField(max_length=200, null=True)
    spatialNorth = CharField(max_length=200, null=True)
    spatialWest = CharField(max_length=200, null=True)
    temporalCoverageBegin = DateTimeField(null=True)
    temporalCoverageEnd = DateTimeField(null=True)
    license = CharField(max_length=200, null=True)
    observation = CharField(max_length=200, null=True)
    publisher = TextField()
    category = CharField(max_length=200, null=True)
    image_uri = TextField(default='/static/img/logo.png')
    sample_rows = JSONField(null=True)
    number_of_rows = CharField(max_length=200, null=True)
    size_in_gb = FloatField(null=True)
    update_frequency = CharField(max_length=200, default='-')
    last_updated = DateTimeField(null=True)
    owner = ForeignKey(User, related_name='dataset_owner', null=True)
    metadata = JSONField(default={})
    arguments = JSONField(default={})
    joined_with_dataset = models.ManyToManyField("self",through = 'JoinOfDatasets',
                                                         symmetrical=False,
                                                        related_name='joined_to')

    organization = ForeignKey(Organization, related_name='datasets', default=1)

    def __str__(self):
        return self.title


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

    @property
    def number_of_rows_formated(self):
        size = long(self.number_of_rows)
        reminder = 0
        power = 1000
        n = 0
        Dic_powerN = {0: '', 1: 'thousand', 2: 'million', 3: 'billion'}
        while size > power:
            reminder = size % power
            size /= power
            n += 1
        return str(float(int(size) + round(float(reminder*0.001), 1))) + " " + Dic_powerN[n]

    def __unicode__(self):
        return self.title

    access_list = ManyToManyField(User, through='DatasetAccess')


class DatasetAccess(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    dataset = ForeignKey(Dataset, on_delete=CASCADE)
    start = DateField()
    end = DateField()
    valid = BooleanField()


class DatasetAccessRequest(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    resource = ForeignKey(Dataset, on_delete=CASCADE, related_name='resource')
    status = CharField(max_length=20, choices=ACCESS_REQUEST_STATUS_CHOICES, default='open')
    creation_date = DateTimeField(default=datetime.now())
    response_date = DateTimeField(null=True)

    @property
    def type(self):
        return 'dataset'



class JoinOfDatasets(Model):
    dataset_first = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='first')
    dataset_second = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='second')
    view_name = models.CharField(max_length=100)


class BaseVariable(Model):
    name = CharField(max_length=256)
    title = CharField(max_length=256)
    unit = CharField(max_length=256)
    description = TextField(null=True)
    sameAs = CharField(null=True, max_length=256)
    dataType = CharField(null=True, max_length=256)
    original_column_name = CharField(null=True, max_length=256)

    class Meta:
        abstract = True


class Dimension(BaseVariable):
    variable = ForeignKey('Variable', related_name='dimensions', on_delete=CASCADE)

    data_column_name = CharField(max_length=255)
    min = DecimalField(blank=True, null=True, default=None, max_digits=100, decimal_places=50)
    max = DecimalField(blank=True, null=True, default=None, max_digits=100, decimal_places=50)
    step = DecimalField(blank=True, null=True, default=None, max_digits=100, decimal_places=50)
    axis = TextField(blank=True, null=True, default=None)
    non_filterable = BooleanField(default=False)

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
            'is_numeric': self.sql_type == 'numeric',
        }

    @property
    def data_column_name(self):
        if self.variable.dataset.stored_at == 'UBITECH_POSTGRES':
            return self.name
        elif self.variable.dataset.stored_at == 'UBITECH_PRESTO':
            return self.name
        else:
            return slugify(self.name, allow_unicode=False).replace('-', '_') + ('_%d' % self.pk)

    @property
    def sql_type(self):
        type_mapping = {}

        if self.unit.startswith('days since ') or \
                self.unit.startswith('hours since ') or \
                self.unit.startswith('minutes since ') or \
                self.unit.startswith('seconds since ') or \
                self.unit.startswith('milliseconds since ') or \
                self.unit == 'timestamp':
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
                 ) and type(value) == int:
            return num2date(value, units=self.unit, calendar=u'gregorian')

        return value

    @property
    def ranges(self):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                MIN(%s),
                MAX(%s)
            FROM %s
        """ % (self.data_column_name, self.data_column_name, self.variable.data_table_name))

        res = cursor.fetchone()

        return {
            'min': self.normalize(res[0]),
            'max': self.normalize(res[1]),
        }

    @property
    def values(self,):
        if self.min is None or self.max is None or self.step is None:
            return self.get_values_from_db()

        if self.step == 0:
            return {
                'min': self.min,
                'max': self.max,
            }

        result = []
        v = self.min
        while v <= self.max:
            result.append(self.normalize(v))
            v += self.step

            # TODO investigate the reason for the following line
            # if v - self.min >= 100:
            #     break

        return result


class Variable(BaseVariable):
    dataset = ForeignKey('Dataset', related_name='variables', on_delete=CASCADE)

    scale_factor = FloatField(default=1)
    add_offset = FloatField(default=0)
    cell_methods = ArrayField(TextField(), null=True)
    type_of_analysis = TextField(blank=True, null=True, default=None)

    # {min, 10%, 25%, 50%, 75%, 90%, max}
    distribution = ArrayField(FloatField(), size=7, blank=True, null=True, default=None)

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
            'is_numeric': True,
        }

    @property
    def safe_name(self):
        return slugify(self.name, allow_unicode=False).replace('-', '_')

    @property
    def data_table_name(self):
        if self.dataset.stored_at == 'UBITECH_POSTGRES':
            return self.dataset.table_name
        elif self.dataset.stored_at == 'UBITECH_PRESTO':
                return self.dataset.table_name
        else:
            return self.safe_name + ('_%d' % self.pk)

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
        cursor.execute("SELECT reltuples::BIGINT AS estimate FROM pg_class WHERE relname='%s'" % self.data_table_name)
        return cursor.fetchone()[0]

    def update_distribution(self, cursor):
        cursor.execute("""
            SELECT
                MIN(value),
                MAX(value),
                percentile_cont(array[0.1, 0.25, 0.5, 0.75, 0.9])
                    within group (order by value)
            FROM %s
        """ % self.data_table_name)

        res = cursor.fetchone()

        if res[0] is None and res[1] is None and res[2] is None:
            self.distribution = [0, 0, 0, 0, 0, 0, 0]
        else:
            self.distribution = [res[0]] + res[2] + [res[1]]

        self.save()


# on variable delete, cleanup
@receiver(pre_delete, sender=Variable)
def log_deleted_question(sender, instance, **kwargs):
    instance.delete_data_table(cursor=connection.cursor())
