from django import forms


class DatasetsForm(forms.Form):
    choices = (
        (u'{"observation": "trip", "source": "anek", "dataType": "csv"}', "ANEK - Trips"),
        (u'{"observation": "history", "source": "anek", "dataType": "csv"}', "ANEK - History"),
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


class FileUploadForm(forms.Form):
    upload = forms.FileField(widget=forms.FileInput(attrs={"id": "file-upload-picker",
                                                           "disabled": True}), label="")


class FileDownloadForm(forms.Form):
    download = forms.CharField(widget=forms.TextInput(attrs={"id": "file-download-url",
                                                             "disabled": True}), label="URL")
    name = forms.CharField(widget=forms.TextInput(attrs={"id": "file-download-name",
                                                         "disabled": True}), label="File Name")
