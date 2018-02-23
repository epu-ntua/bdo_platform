# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from forms import DatasetsForm, FileUploadForm
from requests import Request, Session
from bdo_platform.settings import PARSER_URL


def upload_form(request):
    dataset_form = DatasetsForm()
    file_form = FileUploadForm()

    if request.method == 'GET':
        success_alert = False
    else:
        f = request.FILES['file']
        dataset = request.POST['dataset']

        data = {
            'observation': dataset,
            'type': 'upload'
        }

        files = {'file': f}

        s = Session()
        req = Request('POST', PARSER_URL, data=data, files=files)
        prep = req.prepare()
        resp = s.send(prep)
        s.close()

        success_alert = True

    return render(request, 'upload-form.html', {'dataset_form': dataset_form,
                                                'file_form': file_form,
                                                'success_alert': success_alert})
