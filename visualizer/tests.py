from django.test import TestCase
from query_designer.models import Query
import numpy as np

# Create your tests here.

def trim_year(full_date):
    year = full_date.__str__()
    year = year.split("-")
    return int(year[0])

def get_test_data(markers, ship, minyear, maxyear):
    q = Query.objects.get(pk=2)
    q.document['limit'] = markers
    #return q.execute()['results']
    result = q.execute()['results']
    length = len(result) - 1
    data = []
    for index in range(0, length):
        d = result[index]
        entry_year = trim_year(d[2])
        if ship != "all":
            ship = int(ship)
            if d[1] != ship:
                continue
        if entry_year >= minyear or entry_year <= maxyear:
            #data.append((np.array([float(d[3]), float(d[4]), int(d[1])]) * np.array([1, 1, 1])).tolist())
            data.append([float(d[3]), float(d[4]), int(d[1]), str(d[2])])
    return data
        #import pdb;pdb.set_trace()
