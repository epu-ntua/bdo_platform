from django import forms

class HCMRForm(forms.Form):
    latitude1 = forms.FloatField(label = 'Latitude1:')
    longitude1 = forms.FloatField(label = 'Longitude1:')
    start_date1 = forms.DateField(label='Start Date')
    duration1 = forms.IntegerField(label='Duration in Hours')
    oil_volume1 = forms.FloatField(label='Volume of spilled oil in m3')

    latitude2 = forms.FloatField(label = 'Latitude2:', required=False)
    longitude2 = forms.FloatField(label = 'Longitude2:', required=False)
    start_date2 = forms.DateField(label='Start Date2', required=False)
    duration2 = forms.IntegerField(label='Duration2 in Hours', required=False)
    oil_volume2 = forms.FloatField(label='Volume2 of spilled oil in m3', required=False)

    latitude3 = forms.FloatField(label='Latitude3:', required=False)
    longitude3 = forms.FloatField(label='Longitude3:', required=False)
    start_date3 = forms.DateField(label='Start Date3', required=False)
    duration3 = forms.IntegerField(label='Duration3 in Hours', required=False)
    oil_volume3 = forms.FloatField(label='Volume3 of spilled oil in m3', required=False)

    latitude4 = forms.FloatField(label='Latitude4:', required=False)
    longitude4 = forms.FloatField(label='Longitude4:', required=False)
    start_date4 = forms.DateField(label='Start Date4', required=False)
    duration4 = forms.IntegerField(label='Duration4 in Hours', required=False)
    oil_volume4 = forms.FloatField(label='Volume4 of spilled oil in m3', required=False)

    latitude5 = forms.FloatField(label='Latitude5:', required=False)
    longitude5 = forms.FloatField(label='Longitude5:', required=False)
    start_date5 = forms.DateField(label='Start Date5', required=False)
    duration5 = forms.IntegerField(label='Duration5 in Hours', required=False)
    oil_volume5 = forms.FloatField(label='Volume5 of spilled oil in m3', required=False)

    end_date = forms.DateField(label='End Date')

    oil_density = forms.FloatField(label='Density of spilled oil in kg/m3')
    simulation_length = forms.IntegerField(label='Length of requested simulation  in Hours')
    time_interval = forms.IntegerField(label='Time interval between two outputs in Hours')