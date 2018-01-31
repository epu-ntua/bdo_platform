from query_designer.models import Query

# Create your tests here.

def trim_year(full_date):
    year = full_date.__str__()
    year = year.split("-")
    return int(year[0])

def get_data(markers, ship, minyear, maxyear):
    q = Query.objects.get(pk=2)
    q.document['limit'] = markers
    #import pdb;pdb.set_trace()
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
            data.append([float(d[3]), float(d[4]), int(d[1]), str(d[2]), float(d[0])])
    return data
