# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from forms import DataProviderForm, FilePickerForm
from requests import Request, Session
from bdo_platform.settings import PARSE_URL, PARSER_JWT


def parse_form(request):
    provider_form = DataProviderForm()
    file_form = FilePickerForm()

    submitted_alert = False
    success_alert = False

    if request.method == 'POST':
        # Initialize a session for the request
        s = Session()
        req = Request("POST", PARSE_URL + "/" + request.POST["file"], headers={'Authorization': PARSER_JWT,
                                                                               'Content-Type': 'application/json'})
        prep = req.prepare()
        resp = s.send(prep)

        submitted_alert = True

        if resp.status_code == 200:
            success_alert = True

    return render(request, "parse-form.html", {"provider_form": provider_form,
                                               "file_form": file_form,
                                               "submitted_alert": submitted_alert,
                                               "success_alert": success_alert})
