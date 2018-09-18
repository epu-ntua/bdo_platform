# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from forms import ProfilesForm, FileUploadForm, FileDownloadForm
from requests import Request, Session
from bdo_platform.settings import UPLOAD_WITH_PROFILE_URL, UPLOAD_WITHOUT_PROFILE_URL, DOWNLOAD_URL, PARSER_JWT
import json


def upload_form(request):
    profile_form = ProfilesForm(initial={'profile': -1})
    file_upload_form = FileUploadForm()
    file_download_form = FileDownloadForm()

    submitted_alert = False
    success_alert = False

    if request.method == 'POST':

        # Initialize a session for the request
        s = Session()

        # Retrieve file, if present
        if 'upload' in request.FILES.keys():
            try:
                f = request.FILES['upload']
                files = {'file': f}

                profile = str(request.POST["profile"])
                if profile == '-1':
                    req = Request('POST', UPLOAD_WITHOUT_PROFILE_URL, files=files, headers={'Authorization': PARSER_JWT})

                else:
                    req = Request('POST', UPLOAD_WITH_PROFILE_URL, data= {"profile": profile}, files=files, headers={'Authorization': PARSER_JWT})

                prep = req.prepare()
                resp = s.send(prep, timeout=None)

                if resp.status_code == 200:
                    success_alert = True
            except:
                pass
        else:
            try:
                method = str(request.POST["method"])
                url = str(request.POST["url"])
                directory = str(request.POST["directory"])
                filename = str(request.POST["name"])
                username = str(request.POST["username"])
                password = str(request.POST["password"])
                profile = str(request.POST["profile"])
                print method, url, directory, filename, username, password, profile

                if profile == '-1':
                    metadataProfileId = None
                else:
                    metadataProfileId = profile

                data = dict()
                data["downloadMethod"] = method
                data["downloadURL"] = url
                data["downloadDirectory"] = directory
                data["fileName"] = filename
                data["username"] = username
                data["password"] = password
                data["metadataProfileId"] = metadataProfileId

                req = Request('POST', DOWNLOAD_URL, json=data, headers={'Authorization': PARSER_JWT})
                prep = req.prepare()
                resp = s.send(prep, timeout=None)

                if resp.status_code == 200:
                    success_alert = True
            except:
                pass

        s.close()

        submitted_alert = True

    return render(request, 'upload-form.html', {'profile_form': profile_form,
                                                'upload_form': file_upload_form,
                                                'download_form': file_download_form,
                                                'submitted_alert': submitted_alert,
                                                'success_alert': success_alert})
