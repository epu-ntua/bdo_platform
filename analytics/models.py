from __future__ import unicode_literals

import os
import subprocess
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models import *
from django.utils.timezone import now

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
    service_id = IntegerField()  # to be turned to Foreign Key once services turn into a model
    arguments = JSONField()  # json representation of arguments passed to the analysis
    message = TextField(blank=True, null=True, default=None)  # some progress or error message
    results = JSONField(blank=True, null=True, default=None)  # the results of this job

    @property
    def job_source(self):
        return 'linear_regression'

    def submit(self):
        # mark as started
        self.status = 'STARTED'
        self.started = now()
        self.save()

        # submit to spark cluster
        command = [
            'spark-submit',  # SPARK_SUBMIT_PATH,
            '--driver-class-path=%s' % os.path.join(os.path.join(BASE_DIR, 'drivers'), 'postgresql-42.1.1.jre7.jar'),
            os.path.join(os.path.join(os.path.join(BASE_DIR, 'analytics'), 'jobs'), self.job_source + '.py'),
            str(self.pk),
            SERVER_URL
        ]
        print ' '.join(command)

        # TODO fix in windows
        subprocess.Popen(command)

    def update(self, results, error_msg=''):
        # mark as finished and save results
        self.results = results
        self.status = 'FINISHED' if not error_msg else 'FAILED'
        self.message = error_msg if error_msg else 'Finished'
        self.finished = now()
        self.save()

    def get_absolute_url(self):
        return '/analytics/jobs/%d/' % self.pk
