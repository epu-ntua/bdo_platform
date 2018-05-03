# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models import *

from bdo_main_app.lists import *

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField


class Dashboard(Model):
    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    # dashboard creator
    user = ForeignKey(User)
    title = CharField(max_length=512)

    viz_components = JSONField(default=dict())
    private = BooleanField(default=True)


class ExampleModel(Model):
    content = RichTextUploadingField()


class ExampleNonUploadModel(Model):
    content = RichTextField()