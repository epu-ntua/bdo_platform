from optparse import make_option

from django.core.management.base import BaseCommand
from aggregator.example import pg_example


class Command(BaseCommand):
    help = 'Import example dataset to postgres'

    def handle(self, *args, **options):
        pg_example(stdout=self.stdout)
