from django import forms

class HCMRForm(forms.Form):
    # your_name = forms.CharField(label='Your name', max_length=100)
    latitude = forms.FloatField(label = 'Latitude:')
    longitude = forms.FloatField(label = 'Longitude:')
    start_date = forms.DateField(label='Start Date')
    end_date = forms.DateField(label='End Date')
    duration = forms.IntegerField(label='Duration in Hours')
    oil_volume = forms.FloatField(label='Volume of spilled oil in m3')
    oil_density = forms.FloatField(label='Density of spilled oil in kg/m3')
    simulation_length = forms.IntegerField(label='Length of requested simulation  in Hours')
    time_interval = forms.IntegerField(label='Time interval between two outputs in Hours')