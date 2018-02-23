from django import forms


class DatasetsForm(forms.Form):
    choices = (
        ('trips', 'ANEK - Trips'),
        ('history', 'ANEK - History'),
        ('tanker', 'FOINIKAS - Tanker'),
        ('forecast', 'HCMR - Forecast'),
        ('profile', 'HCMR - Profile'),
        ('timeSeries', 'HCMR - Time Series'),
        ('buoy', 'NESTER - Buoys'),
        ('maretec', 'NESTER - Maretec'),
        ('numerical', 'NESTER - Numerical'),
        ('AIS', 'XMILE - AIS')
    )

    dataset = forms.ChoiceField(widget=forms.Select(attrs={"id": "dataset-dropdown", "name": "dataset-dropdown"}),
                                choices=choices, label="")


class FileUploadForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={"id": "file-upload", "name": "file-upload"}), label="")
