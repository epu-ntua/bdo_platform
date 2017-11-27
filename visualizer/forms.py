from django import forms
from django.forms import NumberInput

from query_designer.models import Query

def populate(mode):
    q = Query.objects.get(pk=2)
    q.document['limit'] = 500
    results = q.execute()['results']
    length = len(results) - 1
    data = []
    min = 9999
    max = 0

    if mode == 'ship':
        data.append(("all", "All Ships"))

    for index in range(0, length):
        d = results[index]
        if mode == 'ship':
            t = (d[1].__str__(), d[1])
            if t not in data:
                data.append(t)
        elif mode == 'year':
            t = d[2].__str__()
            t = t.split("-")
            t = int(t[0])
            if t > max:
                max = t
            elif t < min:
                min = t
    if mode == 'year':
        data = [min, max]

    #import pdb;pdb.set_trace()
    return data

class MapForm(forms.Form):
    choices = (
        ('10', 10),
        ('20', 20),
        ('50', 50),
        ('100', 100),
        ('200', 200),
        ('500', 500),
        ('1000', 1000),
        ('2000', 2000),
        ('10000', 10000),
    )
    maps = {
        ('marker clusters', 'Marker Clusters'),
        ('heatmap', 'Heatmap'),

    }

    year_choices = populate('year')

    ship = forms.ChoiceField(label='Ship Id ', required=False, choices=populate('ship'))
    markers = forms.ChoiceField(label='Markers ', choices=choices, initial='50')
    line = forms.BooleanField(label='Display Course ', initial=True, required=False)
    min_year = forms.IntegerField(label='Min Year', required=False, initial=year_choices[0])
    max_year = forms.IntegerField(label='Max Year', required=False, initial=year_choices[1])
    tiles = forms.ChoiceField(label='Map', choices=maps, initial='tiles')


