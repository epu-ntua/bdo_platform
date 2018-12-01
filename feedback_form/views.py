# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.shortcuts import render

from .forms import FeedbackForm
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail


def feedback_form(request):
    if request.user.is_authenticated():
        username = request.user.username
        if request.method == 'POST':
            form = FeedbackForm(request.POST)

            if form.is_valid():
                form.save()
                # This can be used to send an email to inform us about the newly submitted feedback.
                action = form.cleaned_data['service']
                details = form.cleaned_data['details']
                rating = str(form.cleaned_data['rating'])
                email_text = 'User: "' + str(username) + '" submitted his/her feedback on BDO Platform, regarding action: "' + str(
                    action) + '".\nComment: "' + str(details) + '"\nRating: ' + str(rating) + '/5 stars.'
                send_mail(str(username) + "'s Feedback on BDO Platform", email_text, 'admin@bigdataocean.eu', ['feedback@bigdataocean.eu'],
                          fail_silently=False)
                print email_text
                return render(request, 'feedback_form/thanks.html')
        else:
            form = FeedbackForm()
        return render(request, 'feedback_form/feedback_form.html', {'form': form, 'user':username})
    else:
        raise PermissionDenied