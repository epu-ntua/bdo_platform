# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.shortcuts import render

from .forms import FeedbackForm
from django.core.exceptions import PermissionDenied


def feedback_form(request):
    if request.user.is_authenticated():
        username = request.user.username
        if request.method == 'POST':
            form = FeedbackForm(request.POST)

            if form.is_valid():
                form.save()
                return render(request, 'feedback_form/thanks.html')
        else:
            form = FeedbackForm()
        return render(request, 'feedback_form/feedback_form.html', {'form': form, 'user':username})
    else:
        raise PermissionDenied