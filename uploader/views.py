# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from forms import DatasetsForm, FileUploadForm, FileDownloadForm
from requests import Request, Session
from bdo_platform.settings import UPLOAD_URL, DOWNLOAD_URL, PARSER_JWT
import json


def upload_form(request):
    dataset_form = DatasetsForm()
    file_upload_form = FileUploadForm()
    file_download_form = FileDownloadForm()
    success_alert = False

    if request.method == 'POST':
        # Retrieve data
        data = json.loads(request.POST["dataset"])

        # Initialize a session for the request
        s = Session()

        # Retrieve file, if present
        if 'upload' in request.FILES.keys():
            f = request.FILES['upload']
            files = {'file': f}
            req = Request('POST', UPLOAD_URL, data=data, files=files, headers={'Authorization': PARSER_JWT})
            prep = req.prepare()
            _ = s.send(prep)
        else:
            data["downloadUrl"] = request.POST["download"]
            data["fileName"] = request.POST["name"]

            req = Request('POST', DOWNLOAD_URL, json=data, headers={'Authorization': PARSER_JWT})
            prep = req.prepare()
            _ = s.send(prep)

        s.close()

        success_alert = True

    return render(request, 'upload-form.html', {'dataset_form': dataset_form,
                                                'upload_form': file_upload_form,
                                                'download_form': file_download_form,
                                                'success_alert': success_alert})
