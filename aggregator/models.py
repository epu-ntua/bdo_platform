from django.contrib.postgres.fields import ArrayField
from django.db.models import *
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.db import connection


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
    axis = TextField(blank=True, null=True, default=None)

    @property
    def data_column_name(self):
        return slugify(self.name, allow_unicode=False).replace('-', '_') + ('_%d' % self.pk)

    @property
    def sql_type(self):
        type_mapping = {}

        try:
            return type_mapping[self.name]
        except KeyError:
            return 'numeric'


class Variable(BaseVariable):
    dataset = ForeignKey('Dataset', related_name='variables')

    scale_factor = FloatField(default=1)
    add_offset = FloatField(default=0)
    cell_methods = ArrayField(TextField())
    type_of_analysis = TextField()

    @property
    def data_table_name(self):
        return slugify(self.name, allow_unicode=False).replace('-', '_') + ('_%d' % self.pk)

    def create_data_table(self, cursor):
        # gather columns
        columns = []
        for d in self.dimensions.all():
            columns.append('%s %s' % (d.data_column_name, d.sql_type))
        columns.append('value double precision')

        # create table
        cursor.execute('CREATE TABLE %s (%s);' %
                       (self.data_table_name, ','.join(columns)))

        # add indices
        for column in columns:
            col_name = column.split(' ')[0]
            cursor.execute('CREATE INDEX idx_%d_%s ON %s (%s);' %
                           (self.pk, col_name, self.data_table_name, col_name))

    def delete_data_table(self, cursor):
        # delete indeces
        for d in self.dimensions.all():
            cursor.execute('DROP INDEX IF EXISTS idx_%d_%s;' % (self.pk, d.data_column_name))

        # delete table
        cursor.execute('DROP TABLE IF EXISTS %s;' % self.data_table_name)


# on variable delete, cleanup
@receiver(pre_delete, sender=Variable)
def log_deleted_question(sender, instance, **kwargs):
    instance.delete_data_table(cursor=connection.cursor())
