from django import forms
import requests, json
from bdo_platform.settings import PARSER_JWT, PROFILES_URL


class DatasetsForm(forms.Form):
    choices = (
        (None, ""),
        (u'{"observation": "trip", "source": "anek", "dataType": "csv"}', "ANEK - Trips"),
        (u'{"observation": "history", "source": "anek", "dataType": "csv"}', "ANEK - History"),
        (u'{"observation": "copernicus-baltic-ice-concentration", "source": "copernicus", "dataType": "netcdf"}',
         "Copernicus - Baltic Sea Ice Concentration"),
        (u'{"observation": "copernicus-baltic-ice-thickness", "source": "copernicus", "dataType": "netcdf"}',
         "Copernicus - Baltic Sea Ice Thickness"),
        (u'{"observation": "copernicus-black-sea-insitu", "source": "copernicus", "dataType": "netcdf"}',
         "Copernicus - Black Sea Insitu"),
        (u'{"observation": "copernicus-wave-forecast", "source": "copernicus", "dataType": "netcdf"}',
         "Copernicus - Wave Forecast"),
        (u'{"observation": "tanker", "source": "foinikas", "dataType": "xslx"}', "FOINIKAS - Tanker"),
        (u'{"observation": "forecast", "source": "hcmr", "dataType": "netcdf"}', "HCMR - Forecast"),
        (u'{"observation": "profile", "source": "hcmr", "dataType": "netcdf"}', "HCMR - Profile"),
        (u'{"observation": "timeseries", "source": "hcmr", "dataType": "netcdf"}', "HCMR - Time Series"),
        (u'{"observation": "buoy", "source": "nester", "dataType": "netcdf"}', "NESTER - Buoy"),
        (u'{"observation": "maretec", "source": "nester", "dataType": "netcdf"}', "NESTER - Maretec"),
        (u'{"observation": "numerical", "source": "nester", "dataType": "netcdf"}', "NESTER - Numerical"),
        (u'{"observation": "ais", "source": "xmile", "dataType": "netcdf"}', "XMILE - AIS")
    )

    dataset = forms.ChoiceField(widget=forms.Select(attrs={"id": "dataset-dropdown", "name": "dataset-dropdown"}),
                                choices=choices, label="")


class ProfilesForm(forms.Form):
    choices = [
        (-1, "None"),
    ]

    s = requests.Session()
    req = requests.Request("GET", PROFILES_URL, headers={'Authorization': PARSER_JWT})
    prep = req.prepare()
    resp = s.send(prep, timeout=None)
    if resp.status_code == 200:
        for profile in json.loads(resp.content):
            choices.append((profile["id"], profile["profileName"]))

    profile = forms.ChoiceField(widget=forms.Select(attrs={"id": "profile-dropdown", "name": "profile-dropdown"}),
                                choices=choices, label="")


class FileUploadForm(forms.Form):
    upload = forms.FileField(widget=forms.FileInput(attrs={"id": "file-upload-picker",
                                                           "disabled": False}), label="")


class FileDownloadForm(forms.Form):

    method_choices = [
        ("HTTP", "HTTP"),
        ("FTP", "FTP"),
    ]
    method = forms.ChoiceField(widget=forms.Select(attrs={"id": "file-download-method", "name": "file-download-method",
                                                          "disabled": True}),
                               choices=method_choices, label="Method")

    url = forms.CharField(widget=forms.TextInput(attrs={"id": "file-download-url", "name": "file-download-url",
                                                             "disabled": True}), label="URL")

    directory = forms.CharField(widget=forms.TextInput(attrs={"id": "file-download-directory", "name": "file-download-directory",
                                                             "disabled": True}), label="Directory")

    name = forms.CharField(widget=forms.TextInput(attrs={"id": "file-download-name", "name": "file-download-name",
                                                         "disabled": True}), label="File Name")

    username = forms.CharField(widget=forms.TextInput(attrs={"id": "file-download-username", "name": "file-download-username",
                                                         "disabled": True}), label="Username (optional)", required=False)

    password = forms.CharField(widget=forms.PasswordInput(attrs={"id": "file-download-password", "name": "file-download-password",
                                                         "disabled": True}), label="Password (optional)", required=False)
