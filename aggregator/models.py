from django.contrib.postgres.fields import ArrayField
from django.db.models import *
from django.utils.text import slugify


class Dataset(Model):
    title = TextField()
    source = TextField()
    description = TextField()
    references = ArrayField(TextField())


class BaseVariable(Model):
    name = CharField(max_length=64)
    title = CharField(max_length=128)
    unit = CharField(max_length=64)

    class Meta:
        abstract = True


class Dimension(BaseVariable):
    variable = ForeignKey('Variable', related_name='dimensions')

    data_column_name = CharField(max_length=255)
    min = FloatField(blank=True, null=True, default=None)
    max = FloatField(blank=True, null=True, default=None)
    step = FloatField(blank=True, null=True, default=None)
    axis = TextField()

    @property
    def sql_type(self):
        type_mapping = {}

        try:
            return type_mapping[self.name]
        except KeyError:
            return 'numeric'

    def save(self, *args, **kwargs):
        self.data_column_name = slugify(self.name, allow_unicode=False).replace('-', '_')
        super(Dimension, self).save(*args, **kwargs)


class Variable(BaseVariable):
    dataset = ForeignKey('Dataset', related_name='variables')

    data_table_name = CharField(max_length=255)
    scale_factor = FloatField(default=1)
    add_offset = FloatField(default=0)
    cell_methods = ArrayField(TextField())
    type_of_analysis = TextField()

    def create_data_table(self, cursor):
        # gather columns
        columns = []
        for d in self.dimensions:
            columns.append('%s %s' % (d.data_column_name, d.sql_type))
        columns.append('value double precision')

        # create table
        cursor.execute('CREATE TABLE %s (%s);' %
                       (self.data_table_name, ','.join(columns)))

        # add indices
        for column in columns:
            col_name = column.split(' ')[0]
            cursor.execute('CREATE INDEX idx_%s ON %s (%s);' %
                           (col_name, self.data_table_name, col_name))

    def save(self, *args, **kwargs):
        self.data_table_name = slugify(self.name, allow_unicode=False).replace('-', '_')
        super(Variable, self).save(*args, **kwargs)
