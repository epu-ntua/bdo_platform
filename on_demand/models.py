# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import *
from django.template import defaultfilters
from unidecode import unidecode


class OnDemandRequest(Model):
    """
    A request opened by a user
    """
    created = DateTimeField(auto_now_add=True, db_index=True)
    updated = DateTimeField(auto_now=True, db_index=True)
    user = ForeignKey('auth.User', related_name='on_demand_requests', on_delete=CASCADE)
    title = TextField(db_index=True)
    description = TextField(blank=True)
    keywords_raw = TextField(blank=True)  # comma-separated list of keywords
    pricing = CharField(max_length=8, choices=(
        ('FREE', 'Free'),
        ('FIXED', 'Fixed price'),
        ('TBD', 'Negotiable'),
    ), db_index=True)
    price = DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, default=None)
    closed_by = ForeignKey('OnDemandReply', on_delete=SET_NULL, blank=True, null=True, default=None)

    def __unicode__(self):
        return self.title

    @property
    def slug(self):
        return defaultfilters.slugify(unidecode(self.title[:20]))

    def get_absolute_url(self):
        return '/on-demand/%d/%s/' % (self.pk, self.slug)

    def keywords(self):
        return [keyword.strip() for keyword in self.keywords_raw.split(',')]


class OnDemandReply(Model):
    """
    A reply to an OnDemandRequest
    """
    created = DateTimeField(auto_now_add=True, db_index=True)
    updated = DateTimeField(auto_now=True)
    user = ForeignKey('auth.User', related_name='on_demand_replies', on_delete=CASCADE)
    text = TextField()


class OnDemandUpvote(Model):
    """
    An upvote for an OnDemandRequest
    """
    created = DateTimeField(auto_now_add=True)
    user = ForeignKey('auth.User', related_name='on_demand_upvotes', on_delete=CASCADE)
    request = ForeignKey('OnDemandRequest', related_name='upvotes', on_delete=CASCADE)

