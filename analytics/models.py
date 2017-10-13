from __future__ import unicode_literals

import os, subprocess
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models import *
from django.utils.timezone import now

from bdo_main_app.models import Service
from bdo_platform.settings import BASE_DIR, SERVER_URL, SPARK_SUBMIT_PATH


class JobInstance(Model):
    """

    """
    user = ForeignKey(User, related_name='job_instances')
    submitted = DateTimeField(auto_now_add=True)
    started = DateTimeField(blank=True, null=True, default=None)
    finished = DateTimeField(blank=True, null=True, default=None)
    status = CharField(max_length=32, choices=(
        ('PENDING', 'Pending'),
        ('STARTED', 'Started'),
        ('FINISHED', 'Finished'),
        ('STOPPED', 'Stopped'),
        ('FAILED', 'Failed'),
    ), default='PENDING')
    analysis_flow = JSONField()  # json representation of the process of the
    arguments = JSONField()  # json representation of arguments passed to the analysis
    message = TextField(blank=True, null=True, default=None)  # some progress or error message
    results = JSONField(blank=True, null=True, default=None)  # the results of this job

    @property
    def job_source(self):
        # TODO: maybe to be configured dynamically
        return 'service_building'

    def submit(self):
        # mark as started
        self.status = 'STARTED'
        self.started = now()
        self.save()

        # submit to spark cluster
        command = SPARK_SUBMIT_PATH + ' '  # SPARK_SUBMIT_PATH,
        command += '--driver-class-path=%s ' % os.path.join(os.path.join(BASE_DIR, 'drivers'), 'postgresql-42.1.1.jre7.jar')
        command += ' ' + os.path.join(os.path.join(os.path.join(BASE_DIR, 'analytics'), 'jobs'), self.job_source + '.py')
        command += ' ' + str(self.pk) + ' '
        command += SERVER_URL

        print ' '.join(command)

        try:
            if 'bdo-dev' in SERVER_URL:
                today = datetime.today()
                if not os.path.exists(os.path.join(os.path.join(os.path.join(BASE_DIR, 'analytics'), 'logs'), str(today.month)+'-'+str(today.year))):
                    os.makedirs(os.path.join(os.path.join(os.path.join(BASE_DIR, 'analytics'), 'logs'), str(today.month)+'-'+str(today.year)))
                logs_dir = os.path.join(os.path.join(os.path.join(BASE_DIR, 'analytics'), 'logs'), str(today.month)+'-'+str(today.year))
                with open(os.path.join(logs_dir, "logfile_analysis_"+str(self.pk)), 'w+') as f:
                    subprocess.Popen(command, shell=True, stdout=f, stderr=f)
            else:
                subprocess.Popen(command, shell=True)
        except Exception as e:
            print('ERROR')
            print e
            # mark as failed
            self.status = 'FAILED'
            self.finished = now()
            self.save()

    def update(self, results, error_msg=''):
        # mark as finished and save results
        self.results = results
        self.status = 'FINISHED' if not error_msg else 'FAILED'
        self.message = error_msg if error_msg else 'Finished'
        self.finished = now()
        self.save()

    def get_absolute_url(self):
        return '/analytics/jobs/%d/' % self.pk

    def __unicode__(self):
        return '%s -> %s' % (self.user.username, str(self.base_analysis))
