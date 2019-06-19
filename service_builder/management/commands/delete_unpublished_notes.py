from django.core.management.base import BaseCommand, CommandError
from service_builder.models import *
from datetime import tzinfo, timedelta, datetime
from visualizer.utils import delete_zep_notebook
from django.utils import timezone


class Command(BaseCommand):
    help = 'Deletes the zeppelin notebooks for all unpublished and old services'

    def handle(self, *args, **options):
        services = Service.objects.filter(published=False)
        for s in services:
            created = s.created
            elapsedTime = timezone.now() - created
            if elapsedTime.total_seconds() > 600:
                delete_zep_notebook(s.notebook_id)
        self.stdout.write(self.style.SUCCESS('SUCCESS'))
