# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from django.shortcuts import render, redirect

from .models import *
from .forms import *
from django.dispatch.dispatcher import receiver
from allauth.account.signals import email_confirmed


@receiver(email_confirmed, dispatch_uid="unique")
def user_logged_in_(request, **kwargs):
    user = kwargs['email_address'].user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user)
    profile.first_name = user.first_name
    profile.last_name = user.last_name
    profile.email = user.email
    profile.save()


def show_profile(request, username):
    user = User.objects.get(username=username)

    return render(request, 'profile/index.html', {
        'user': user,
    })


@login_required
def update_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save()
            user = request.user
            if user.email is None or user.email == '':
                if form.cleaned_data['email'].strip() != '':
                    user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            print "email: " + str(user.email)
            print str(user.email.strip()) != ''
            if user.email is not None and str(user.email.strip()) != '':
                try:
                    email_address = EmailAddress.objects.get(user=user)
                    email_address.email = user.email
                except EmailAddress.DoesNotExist:
                    email_address = EmailAddress(user=user, email=user.email, primary=True)
                email_address.save()
            return redirect(profile.get_absolute_url())
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profile/edit.html', {
        'user': request.user,
        'form': form,
    })
