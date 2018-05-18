# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db.models import *

from s3direct.fields import S3DirectField

from bdo_platform.settings import S3DIRECT_REGION, AWS_STORAGE_BUCKET_NAME


class UserProfile(Model):
    user = OneToOneField('auth.User', related_name='userprofile', on_delete=CASCADE)
    avatar_raw = S3DirectField(dest='avatars', blank=True, null=True, default=None)
    first_name = TextField(blank=True, default='')
    last_name = TextField(blank=True, default='')
    organization = TextField(blank=True, default='')
    user_type = CharField(max_length=32, choices=(
        ('DATA_ANALYST', 'Data analyst'),
        ('BUSINESS_USER', 'Business user'),
        ('RESEARCHER', 'Researcher'),
        ('SERVICE_DEVELOPER', 'Service developer'),
    ), default='DATA_ANALYST')
    business_role = TextField(blank=True, default='')
    email = EmailField(blank=True, default='')
    external_url = URLField(blank=True, default='')

    def get_absolute_url(self):
        return '/profile/%s/' % self.user.username

    @property
    def avatar(self):
        return self.avatar_raw or (
            'https://s3.%s.amazonaws.com/%s/avatars/default-avatar.png' % (S3DIRECT_REGION, AWS_STORAGE_BUCKET_NAME)
        )


@property
def get_or_create_profile(user):
    try:
        p = user._profile
    except AttributeError:
        p, _ = UserProfile.objects.get_or_create(user=user)
        setattr(user, '_profile', p)

    return p


# define user.profile
User.profile = get_or_create_profile
