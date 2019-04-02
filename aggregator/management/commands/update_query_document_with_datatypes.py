from django.core.management.base import BaseCommand
from query_designer.models import *
from aggregator.models import *
from django.conf import settings

class Command(BaseCommand):
    help = 'Updates the saved query documents to include the variables/dimensions data types'

    def handle(self, *args, **options):
        for q in AbstractQuery.objects.all():
            doc = q.document
            for f in doc['from']:
                for s in f['select']:
                    try:
                        if s['type'] == "VALUE":
                            s['datatype'] = str(Variable.objects.get(pk=int(f['type'])).dataType)
                        else:
                            s['datatype'] = str(Dimension.objects.get(pk=int(s['type'])).dataType)
                    except:
                        pass
        q.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated all the queries'))
