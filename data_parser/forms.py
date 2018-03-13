from django import forms


class DataProviderForm(forms.Form):
    choices = (
        (None, ""),
        ("trip", "ANEK - Trips"),
        ("history", "ANEK - History"),
        ("tanker", "FOINIKAS - Tanker"),
        ("forecast", "HCMR - Forecast"),
        ("profile", "HCMR - Profile"),
        ("timeseries", "HCMR - Time Series"),
        ("buoy", "NESTER - Buoys"),
        ("maretec", "NESTER - Maretec"),
        ("numerical", "NESTER - Numerical"),
        ("ais", "XMILE - AIS")
    )

    provider = forms.ChoiceField(widget=forms.Select(attrs={"id": "provider-dropdown"}), choices=choices, label="")


class FilePickerForm(forms.Form):
    file = forms.ChoiceField(widget=forms.Select(attrs={"id": "file-dropdown"}), label="")
