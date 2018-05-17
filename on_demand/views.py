# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from .models import *
from .forms import *


class OnDemandRequestListView(ListView):
    template_name = 'on_demand/list.html'
    model = OnDemandRequest
    paginate_by = 1


def on_demand_create(request):
    if request.method == 'POST':
        form = OnDemandRequestForm(request.POST)

        # validate & save
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user
            req.save()

            return redirect(req.get_absolute_url())
    else:
        form = OnDemandRequestForm()

    return render(request, 'on_demand/create.html', {
        'form': form,
    })


class OnDemandRequestDetailView(DetailView):
    model = OnDemandRequest
    template_name = 'on_demand/details.html'
