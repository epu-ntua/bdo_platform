# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from .models import *
from .forms import *


class OnDemandRequestListView(ListView):
    template_name = 'on_demand/list.html'
    model = OnDemandRequest
    paginate_by = 10

    def get_queryset(self):
        queryset = super(OnDemandRequestListView, self).get_queryset()

        # text search
        q = self.request.GET.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(description__icontains=q) | Q(keywords_raw__icontains=q)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super(OnDemandRequestListView, self).get_context_data(**kwargs)

        # add search term
        context['q'] = self.request.GET.get('q', '')

        return context


@login_required
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

    return render(request, 'on_demand/form.html', {
        'form': form,
        'action': 'create',
    })


@login_required
def on_demand_update(request, pk):
    req = OnDemandRequest.objects.get(pk=pk, user=request.user)

    if request.method == 'POST':
        form = OnDemandRequestForm(request.POST, instance=req)

        # validate & save
        if form.is_valid():
            req = form.save()

            return redirect(req.get_absolute_url())
    else:
        form = OnDemandRequestForm(instance=req)

    return render(request, 'on_demand/form.html', {
        'form': form,
        'action': 'update',
    })


class OnDemandRequestDetailView(DetailView):
    model = OnDemandRequest
    template_name = 'on_demand/details.html'


@login_required
def send_reply(request, pk):
    req = OnDemandRequest.objects.get(pk=pk)

    if request.method == 'POST':
        form = OnDemandReplyForm(request.POST)

        # validate & save
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.request = req
            reply.save()

    return redirect(req.get_absolute_url())
