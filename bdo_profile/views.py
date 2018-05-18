# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .models import *
from .forms import *


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

            return redirect(profile.get_absolute_url())
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'profile/edit.html', {
        'user': request.user,
        'form': form,
    })
