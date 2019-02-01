from django import forms

class HCMRForm(forms.Form):
    latitude1 = forms.FloatField(label = 'Latitude1:')
    latitude2 = forms.FloatField(label='Latitude2:', required=False)
    longitude1 = forms.FloatField(label = 'Longitude1:')
    longitude2 = forms.FloatField(label = 'Longitude2:', required=False)
    start_date = forms.DateField(label='Start Date')
    end_date = forms.DateField(label='End Date')
    duration = forms.IntegerField(label='Duration in Hours')
    oil_volume = forms.FloatField(label='Volume of spilled oil in m3')
    oil_density = forms.FloatField(label='Density of spilled oil in kg/m3')
    simulation_length = forms.IntegerField(label='Length of requested simulation  in Hours')
    time_interval = forms.IntegerField(label='Time interval between two outputs in Hours')