import json

from datetime import datetime

from query_designer.models import Query

# Create your tests here.


def filldate(date, mode):
    date = date.split(" ")
    time = []
    if len(date) > 1:
        time = date[1].split(':')
    date = date[0].split('-')
    if len(date) == 1:
        newdate = date[0]
        if mode == 'min':
            newdate = newdate + "-01-01 00:00:00"
        else:
            newdate = newdate + "-12-31 23:59:59"
    elif len(date) == 2:
        newdate = date[0] + "-" + date[1]
        if mode == 'min':
            newdate = newdate + "-01 00:00:00"
        else:
            newdate = newdate + "-31 23:59:59"
    else:
        newdate = date[0] + "-" + date[1] + "-" + date[2] + " "
        if len(time) == 0:
            if mode == 'min':
                newdate = newdate + "00:00:00"
            else:
                newdate = newdate + "23:59:59"
        elif len(time) == 1:
            if mode == 'min':
                newdate = newdate + time[0] + ":00:00"
            else:
                newdate = newdate + time[0] + ":59:59"
        else :
            if mode == 'min':
                newdate = newdate + time[0] + ":" + time[1] + ":00"
            else:
                newdate = newdate + time[0] + ":" + time[1] + ":59"

    return newdate

def get_data(query_pk, markers, ship, mindate, maxdate):
    q = Query.objects.get(pk=query_pk)
    q = Query(document=q.document)
    q.document['limit'] = markers
    filters = {}
    mindate = filldate(mindate, "min")
    maxdate = filldate(maxdate, "max")

    mindate = datetime.strptime(mindate, '%Y-%m-%d %H:%M:%S')
    maxdate = datetime.strptime(maxdate, '%Y-%m-%d %H:%M:%S')
    if ship != 'all':
        filters = {"a": "i0_ship_id", "b": ship, "op": "eq"}
        #q.document["filters"] = {"a": "i0_timestamp", "b": mindate, "op": "gt"}
        #q.document["filters"] = {"a": "i0_timestamp", "b": maxdate, "op": "lt"}
    q.document['filters'] = filters

    result = q.execute()[0]['results']
    print result[:3]

    result_headers = q.execute(only_headers=True)[0]['headers']
    for idx, c in enumerate(result_headers['columns']):
        if str(c['name']).find('lat') >= 0:
            lat_index = idx
        elif str(c['name']).find('lon') >= 0:
            lon_index = idx
        elif str(c['name']).find('ship') >= 0:
            ship_index = idx
        elif str(c['name']).find('timestamp') >= 0:
            time_index = idx
        elif str(c['isVariable']) == 'True':
            var_index = idx

    print result_headers, lat_index, lon_index, ship_index, time_index, var_index

    return {"data": result, "var": var_index, "ship": ship_index, "time": time_index, "lat": lat_index, "lon": lon_index}
