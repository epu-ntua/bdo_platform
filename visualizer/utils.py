import json

from django.contrib.auth.models import User
from django.http import HttpResponse

from query_designer.models import Query
import numpy as np
from math import floor, ceil
import folium.plugins as plugins
import folium
from PIL import Image, ImageChops
import numpy as np
import requests


def fig2data(fig):
    """
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw()

    # Get the RGBA buffer from the figure
    w, h = fig.canvas.get_width_height()
    buf = np.fromstring(fig.canvas.tostring_argb(), dtype=np.uint8)
    buf.shape = (w, h, 4)

    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = np.roll(buf, 3, axis=2)
    return buf


def fig2img ( fig ):
    """
    @brief Convert a Matplotlib figure to a PIL Image in RGBA format and return it
    @param fig a matplotlib figure
    @return a Python Imaging Library ( PIL ) image
    """
    # put the figure pixmap into a numpy array
    buf = fig2data ( fig )
    w, h, d = buf.shape
    return Image.fromstring( "RGBA", ( w ,h ), buf.tostring( ) )


def get_test_data(query, user):
    if str(query).isdigit():
        q = Query.objects.get(pk=int(query))
        result_json = q.execute()
        return result_json['headers'], result_json['results']
    else:
        print 'het'
        print 'query: ' + query
        q = Query(user=User.objects.get(username='BigDataOcean'), document=json.loads(str(query).replace('%20', ' ')))
        # q = Query(user=User.objects.get(username='BigDataOcean'))
        # doc = json.loads(request.POST.get('document', ''))
        print q
        result_json = q.execute()
        return result_json['headers'], result_json['results']


def filter_data(d, other_dims, other_dims_first_vals):
    for dim, val in zip(other_dims, other_dims_first_vals):
        if str(d[dim]) != val:
            return 1
    return 0


def trim(img):
    border = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, border)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        img = img.crop(bbox)
    return np.array(img)


def create_grid_data(lats, lons, data):
    grid = list()
    grid_count = list()
    for i in range(0, len(lons)):
        grid_row = list()
        grid_count_row = list()
        for j in range(0, len(lats)):
            grid_row.append(None)
            grid_count_row.append(0)
        grid.append(grid_row)
        grid_count.append(grid_count_row)

    for item in data:
        j = 0
        for l in lats:
            if item[0] < l:
                j += 1
        i = 0
        for l in lons:
            if item[1] < l:
                i += 1

        if grid[i][j] is None:
            grid[i][j] = item[2]
            grid_count[i][j] = 1
        else:
            grid[i][j] += item[2]
            grid_count[i][j] += 1

    for i in range(0, len(lons)):
        for j in range(0, len(lats)):
            if grid_count[i][j] > 0:
                grid[i][j] /= grid_count[i][j]

    # print grid
    # print grid_count
    return grid


# TODO: replace 100 and make it configurable
def create_bins(list, step):
    return np.arange(floor(list.min() * 100) / 100, ceil(list.max() * 100) / 100 + 0.00001, step)


def create_folium_map(location=[0,0], zoom_start=2, max_zoom=13):
    tiles_str = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token='
    token_str = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ'
    attr_str = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors, ' \
               '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' \
               'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>'

    m = folium.Map(location=location,
                   zoom_start=zoom_start,
                   max_zoom=max_zoom,
                   tiles=tiles_str + token_str,
                   attr=attr_str,
                   control_scale=True)

    # folium.TileLayer('openstreetmap').add_to(m)

    plugins.Fullscreen(
        position='topright',
        title='Expand',
        title_cancel='Exit',
        force_separate_button=True).add_to(m)
    return m


def create_zep_note(name):
    data = dict()
    data['name'] = name
    str_data = json.dumps(data)
    # Make a post request
    response = requests.post("http://localhost:8080/api/notebook", data=str_data)
    print response
    response_json = response.json()
    notebook_id = response_json['body']
    print notebook_id
    return notebook_id


def create_zep_test_query_paragraph(notebook_id, title, raw_query):
    data = dict()
    data['title'] = title
    data['text'] = '%spark.pyspark' \
                   '\ndf = spark.read.format("jdbc")' \
                   '.option("url", "jdbc:postgresql://localhost:5432/bdo_platform?user=postgres&password=1234")' \
                   '.option("driver", "org.postgresql.Driver")' \
                   '.option("database", "bdo_platform")' \
                   '.option("dbtable", "(SELECT * FROM (SELECT temperature.value AS i0_value,temperature.time_4 AS i0_time,temperature.depth_5 AS i0_depth,temperature.lat_6 AS i0_location_latitude,temperature.lon_7 AS i0_location_longitude FROM votemper_2 AS temperature LIMIT 10 ) AS SQ1 ) AS SPARKQ0")' \
                   '.load()' \
                   '\ndf.printSchema()'

    str_data = json.dumps(data)
    response = requests.post("http://localhost:8080/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = response.json()
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def create_zep__query_paragraph(notebook_id, title, raw_query):
    data = dict()
    data['title'] = title
    data['text'] = '%spark.pyspark' \
                   '\ndf = spark.read.format("jdbc")' \
                   '.option("url", "jdbc:postgresql://localhost:5432/bdo_platform?user=postgres&password=1234")' \
                   '.option("driver", "org.postgresql.Driver")' \
                   '.option("database", "bdo_platform")' \
                   '.option("dbtable", "(' + str(raw_query).replace("\n", " ") + ') AS SPARKQ0")' \
                   '.load()' \
                   '\ndf.printSchema()'

    str_data = json.dumps(data)
    response = requests.post("http://localhost:8080/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = response.json()
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def run_zep_paragraph(notebook_id, paragraph_id):
    response_status = 500
    counter = 3
    while response_status != 200:
        data = dict()
        str_data = json.dumps(data)
        response = requests.post("http://localhost:8080/api/notebook/run/" + str(notebook_id) + "/" + str(paragraph_id), data=str_data)
        print response
        counter -= 1
        if counter < 0:
            return HttpResponse(status=500)
        response_status = response.status_code


def create_zep_viz_paragraph(notebook_id, title):
    data = dict()
    data['title'] = 'bdo_test_paragraph'
    data['text'] = '%sql' \
                   '\nselect * from tempTablePostgres'
    str_data = json.dumps(data)
    response = requests.post("http://localhost:8080/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = response.json()
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def create_zep_sort_paragraph(notebook_id, title, sort_col):
    data = dict()
    data['title'] = 'bdo_test_paragraph'
    data['text'] = '%spark.pyspark' \
                   '\ndf = df.sort("' + sort_col + '")'
    str_data = json.dumps(data)
    response = requests.post("http://localhost:8080/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = response.json()
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def create_zep_reg_table_paragraph(notebook_id, title):
    data = dict()
    data['title'] = 'bdo_test_paragraph'
    data['text'] = '%spark.pyspark' \
                   '\ndf.registerTempTable("tempTablePostgres")'

    str_data = json.dumps(data)
    response = requests.post("http://localhost:8080/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = response.json()
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def set_zep_paragraph_line_chart(notebook_id, paragraph_id, query_doc, y_vars, x_var):
    config = {
        "results": {
            "0": {
                "graph": {
                    "mode": "lineChart",
                    "height": 300.0,
                    "optionOpen": 'true',
                    "keys": [{
                        "name": "i0_time",
                        "index": 1.0,
                        "aggr": "sum"
                    }],
                    "values": [{
                        "name": "i0_value",
                        "index": 0.0,
                        "aggr": "sum"
                    }],
                    "groups": []
                },
                "helium": {}
            }
        }
    }
    x_index = -1
    y_index = -1
    counter = 0
    for from_i in query_doc['from']:
        for select_i in from_i['select']:
            if select_i['name'] == x_var:
                x_index = counter
            if select_i['name'] == y_vars:
                y_index = counter
            counter += 1

    x_config_list = []
    x_config = dict()
    x_config['name'] = x_var
    x_config['index'] = float(x_index)
    x_config['aggr'] = 'sum'
    x_config_list.append(x_config)
    config["results"]["0"]["graph"]["keys"] = x_config_list

    y_config_list = []
    y_config = dict()
    y_config['name'] = y_vars
    y_config['index'] = float(y_index)
    y_config['aggr'] = 'sum'
    y_config_list.append(y_config)
    config["results"]["0"]["graph"]["values"] = y_config_list

    str_config = json.dumps(config)
    response = requests.put("http://localhost:8080/api/notebook/" + str(notebook_id) + "/paragraph/" + str(paragraph_id) + "/config", data=str_config)
    print response.json()


def set_zep_paragraph_bar_chart(notebook_id, paragraph_id, query_doc, y_vars, x_var):
    config = {
        "results": {
            "0": {
                "graph": {
                    "mode": "multiBarChart",
                    "height": 300.0,
                    "optionOpen": 'true',
                    "keys": [{
                        "name": "i0_time",
                        "index": 1.0,
                        "aggr": "sum"
                    }],
                    "values": [{
                        "name": "i0_value",
                        "index": 0.0,
                        "aggr": "sum"
                    }],
                    "groups": []
                },
                "helium": {}
            }
        }
    }
    x_index = -1
    y_index = -1
    counter = 0
    for from_i in query_doc['from']:
        for select_i in from_i['select']:
            if select_i['name'] == x_var:
                x_index = counter
            if select_i['name'] == y_vars:
                y_index = counter
            counter += 1

    x_config_list = []
    x_config = dict()
    x_config['name'] = x_var
    x_config['index'] = float(x_index)
    x_config['aggr'] = 'sum'
    x_config_list.append(x_config)
    config["results"]["0"]["graph"]["keys"] = x_config_list

    y_config_list = []
    y_config = dict()
    y_config['name'] = y_vars
    y_config['index'] = float(y_index)
    y_config['aggr'] = 'sum'
    y_config_list.append(y_config)
    config["results"]["0"]["graph"]["values"] = y_config_list

    str_config = json.dumps(config)
    response = requests.put("http://localhost:8080/api/notebook/" + str(notebook_id) + "/paragraph/" + str(paragraph_id) + "/config", data=str_config)
    print response.json()


def set_zep_paragraph_area_chart(notebook_id, paragraph_id, query_doc, y_vars, x_var):
    config = {
        "results": {
            "0": {
                "graph": {
                    "mode": "stackedAreaChart",
                    "height": 300.0,
                    "optionOpen": 'true',
                    "keys": [{
                        "name": "i0_time",
                        "index": 1.0,
                        "aggr": "sum"
                    }],
                    "values": [{
                        "name": "i0_value",
                        "index": 0.0,
                        "aggr": "sum"
                    }],
                    "groups": []
                },
                "helium": {}
            }
        }
    }
    x_index = -1
    y_index = -1
    counter = 0
    for from_i in query_doc['from']:
        for select_i in from_i['select']:
            if select_i['name'] == x_var:
                x_index = counter
            if select_i['name'] == y_vars:
                y_index = counter
            counter += 1

    x_config_list = []
    x_config = dict()
    x_config['name'] = x_var
    x_config['index'] = float(x_index)
    x_config['aggr'] = 'sum'
    x_config_list.append(x_config)
    config["results"]["0"]["graph"]["keys"] = x_config_list

    y_config_list = []
    y_config = dict()
    y_config['name'] = y_vars
    y_config['index'] = float(y_index)
    y_config['aggr'] = 'sum'
    y_config_list.append(y_config)
    config["results"]["0"]["graph"]["values"] = y_config_list

    str_config = json.dumps(config)
    response = requests.put("http://localhost:8080/api/notebook/" + str(notebook_id) + "/paragraph/" + str(paragraph_id) + "/config", data=str_config)
    print response.json()


def set_zep_paragraph_scatter_chart(notebook_id, paragraph_id, query_doc, y_vars, x_var):
    config = {
        "results": {
            "0": {
                "graph": {
                    "mode": "scatterChart",
                    "height": 300.0,
                    "optionOpen": 'true',
                    "keys": [
                        {
                            "index": 3,
                            "name": "i0_location_latitude",
                            "aggr": "sum"
                        }
                    ],
                    "values": [
                        {
                            "index": 0,
                            "name": "i0_value",
                            "aggr": "sum"
                        }
                    ],
                    "groups": [],
                    "setting": {
                        "scatterChart": {
                            "yAxis": {
                                "name": "i0_value",
                                "index": 0,
                                "aggr": "sum"
                            },
                            "xAxis": {
                                "name": "i0_location_latitude",
                                "index": 3,
                                "aggr": "sum"
                            }
                        }
                    }
                },
                "helium": {}
            }
        }
    }
    x_index = -1
    y_index = -1
    counter = 0
    for from_i in query_doc['from']:
        for select_i in from_i['select']:
            if select_i['name'] == x_var:
                x_index = counter
            if select_i['name'] == y_vars:
                y_index = counter
            counter += 1

    x_config_list = []
    x_config = dict()
    x_config['name'] = x_var
    x_config['index'] = float(x_index)
    x_config['aggr'] = 'sum'
    x_config_list.append(x_config)
    config["results"]["0"]["graph"]["keys"] = x_config_list
    config["results"]["0"]["graph"]["setting"]["scatterChart"]["xAxis"] = x_config_list[0]

    y_config_list = []
    y_config = dict()
    y_config['name'] = y_vars
    y_config['index'] = float(y_index)
    y_config['aggr'] = 'sum'
    y_config_list.append(y_config)
    config["results"]["0"]["graph"]["values"] = y_config_list
    config["results"]["0"]["graph"]["setting"]["scatterChart"]["yAxis"] = y_config_list[0]

    str_config = json.dumps(config)
    response = requests.put("http://localhost:8080/api/notebook/" + str(notebook_id) + "/paragraph/" + str(paragraph_id) + "/config", data=str_config)
    print response.json()


def set_zep_paragraph_pie_chart(notebook_id, paragraph_id, query_doc, value_vars, key_var):
    config = {
        "results": {
            "0": {
                "graph": {
                    "mode": "pieChart",
                    "height": 300.0,
                    "optionOpen": 'true',
                    "keys": [{
                        "name": "i0_time",
                        "index": 1.0,
                        "aggr": "sum"
                    }],
                    "values": [{
                        "name": "i0_value",
                        "index": 0.0,
                        "aggr": "sum"
                    }],
                    "groups": []
                },
                "helium": {}
            }
        }
    }
    x_index = -1
    y_index = -1
    counter = 0
    for from_i in query_doc['from']:
        for select_i in from_i['select']:
            if select_i['name'] == key_var:
                x_index = counter
            if select_i['name'] == value_vars:
                y_index = counter
            counter += 1

    x_config_list = []
    x_config = dict()
    x_config['name'] = key_var
    x_config['index'] = float(x_index)
    x_config['aggr'] = 'sum'
    x_config_list.append(x_config)
    config["results"]["0"]["graph"]["keys"] = x_config_list

    y_config_list = []
    y_config = dict()
    y_config['name'] = value_vars
    y_config['index'] = float(y_index)
    y_config['aggr'] = 'sum'
    y_config_list.append(y_config)
    config["results"]["0"]["graph"]["values"] = y_config_list

    str_config = json.dumps(config)
    response = requests.put("http://localhost:8080/api/notebook/" + str(notebook_id) + "/paragraph/" + str(paragraph_id) + "/config", data=str_config)
    print response.json()


def restart_zep_interpreter(interpreter_id):
    interpreter_id = '2D6CA11G8'
    response = requests.put("http://localhost:8080/api/interpreter/setting/restart/"+interpreter_id)
    print response


def create_zep_drop_all_paragraph(notebook_id, title):
    data = dict()
    data['title'] = 'bdo_test_paragraph'
    data['text'] = '%spark.pyspark' \
                   '\nsqlContext.dropTempTable("tempTablePostgres")' \
                   '\ndf=None'

    str_data = json.dumps(data)
    response = requests.post("http://localhost:8080/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = response.json()
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def create_zep_toJSON_paragraph(notebook_id, title):
    data = dict()
    data['title'] = 'bdo_test_paragraph'
    data['text'] = '%spark.pyspark' \
                   '\ndf.toJSON().collect()'

    str_data = json.dumps(data)
    response = requests.post("http://localhost:8080/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = response.json()
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def get_zep_toJSON_paragraph_response(notebook_id, paragraph_id):
    response = requests.get("http://localhost:8080/api/notebook/" + str(notebook_id) + "/paragraph/"+str(paragraph_id))
    print response
    response_json = response.json()
    json_data = response_json['body']['results']['msg'][0]['data']
    print json_data
    return json_data


def create_livy_session(kind):
    host = 'http://bdo-dev.epu.ntua.gr:8998'
    headers = {'Content-Type': 'application/json'}

    data = {'kind': kind}
    response = requests.post(host + '/sessions', data=json.dumps(data), headers=headers).json()
    print response
    try:
        session_id = response['id']
        state = ''
        while state != 'idle':
            state = requests.get(host + '/sessions/' + str(session_id) + '/state', headers=headers).json()['state']
            if state == 'error' or state == 'dead':
                raise Exception('Failed')
    except Exception:
        raise Exception('Failed')
    return session_id


def create_livy_query_statement(session_id, raw_query):
    host = 'http://bdo-dev.epu.ntua.gr:8998'
    headers = {'Content-Type': 'application/json'}
    raw_query = '(SELECT * FROM (SELECT * from wind_speed_11) AS SQ1 LIMIT 1000000) AS tmp'
    data = dict()
    data['code'] = 'df = spark.read.format("jdbc")' \
                   '.option("url", "jdbc:postgresql://localhost:5432/bdo_platform?user=postgres&password=bdo!")' \
                   '.option("driver", "org.postgresql.Driver")' \
                   '.option("database", "bdo_platform")' \
                   '.option("dbtable", "' + str(raw_query).replace("\n", " ") + '")' \
                   '.load()' \
                   '\n#df.show()'

    statements_url = host + '/sessions/%d/statements' % session_id
    response = requests.post(statements_url, data=json.dumps(data), headers=headers).json()
    print response
    try:
        statement_id = response['id']
        state = ''
        while state != 'available':
            state = requests.get(host + '/sessions/' + str(session_id) + '/statements/' + str(statement_id), headers=headers).json()['state']
            if state == 'error' or state == 'cancelling' or state == 'cancelled':
                raise Exception('Failed')
    except Exception:
        raise Exception('Failed')
    return statement_id


def create_livy_toJSON_paragraph(session_id):
    host = 'http://bdo-dev.epu.ntua.gr:8998'
    headers = {'Content-Type': 'application/json'}

    data = dict()
    data['code'] = 'df.toJSON().collect()'

    statements_url = host + '/sessions/%d/statements' % session_id
    response = requests.post(statements_url, data=json.dumps(data), headers=headers).json()
    print response
    try:
        statement_id = response['id']
        state = ''
        while state != 'available':
            response = requests.get(host + '/sessions/' + str(session_id) + '/statements/' + str(statement_id), headers=headers).json()
            state = response['state']
            if state == 'error' or state == 'cancelling' or state == 'cancelled':
                raise Exception('Failed')
    except Exception:
        raise Exception('Failed')
    return response['output']['data']
