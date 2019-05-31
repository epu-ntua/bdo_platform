import json
from django.contrib.auth.models import User
from django.http import HttpResponse
from PIL import Image, ImageChops
from query_designer.models import Query, AbstractQuery
import numpy as np
from math import floor, ceil
import folium.plugins as plugins
import folium
import numpy as np
import requests
import collections
from django.db import connections
from django.conf import settings
from service_builder.models import ServiceInstance
import ast

def convert_unicode_json(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert_unicode_json, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert_unicode_json, data))
    else:
        return data

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
    response = requests.post(settings.ZEPPELIN_URL+"/api/notebook", data=str_data)
    print response
    response_json = response.json()
    notebook_id = response_json['body']
    print notebook_id
    return notebook_id


def clone_zep_note(notebook_id, name):
    data = dict()
    data['name'] = name
    str_data = json.dumps(data)
    # Make a post request
    response = requests.post(settings.ZEPPELIN_URL+"/api/notebook/"+notebook_id, data=str_data)
    print response
    response_json = response.json()
    notebook_id = response_json['body']
    print notebook_id
    return notebook_id


def run_zep_note(notebook_id, exclude=[], mode='zeppelin'):
    if mode == 'livy':
        session_id = create_livy_session(notebook_id)
    response_status = 500
    # number of tries
    counter = 1
    paragraphs = []
    response = requests.get(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id))
    response_json = response.json()
    for p in response_json['body']['paragraphs']:
        if str(p['id']) not in exclude:
            paragraphs.append(p['id'])
        else:
            print 'excluded paragraph: {0}'.format(str(p['id']))
    if mode == 'livy':
        for p in paragraphs:
            run_result = run_zep_paragraph(notebook_id, p, session_id, mode)
        return session_id
    else:
        for p in paragraphs:
            run_result = run_zep_paragraph(notebook_id, p, 0, mode, 1)
            if run_result == 1:
                paragraphs = []
                response = requests.get(settings.ZEPPELIN_URL + "/api/notebook/" + str(notebook_id))
                response_json = response.json()
                for p in response_json['body']['paragraphs']:
                    if str(p['id']) not in exclude:
                        paragraphs.append(p['id'])
                    else:
                        print 'excluded paragraph: {0}'.format(str(p['id']))
                for p in paragraphs:
                    run_result = run_zep_paragraph(notebook_id, p, 0, mode, 2)
                break
        return 0

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


def create_zep_arguments_paragraph(notebook_id, title, args_json_string):
    data = dict()
    data['title'] = title
    data['index'] = 1
    data['text'] = '%spark.pyspark' \
                   '\nimport json' \
                   '\narguments = dict()' \
                   '\nresult = dict()' \
                   '\narguments = json.loads(\'{0}\')' \
                   '\nprint arguments'.format(args_json_string)
    print args_json_string
    str_data = json.dumps(data)
    response = requests.post(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = response.json()
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def create_zep__query_paragraph(notebook_id, title, raw_query, index=-1, df_name="df"):
    data = dict()
    if index >= 0:
        data['index'] = index
    data['title'] = title
    conn_dict = connections[settings.ZEPPELIN_DB].settings_dict
    data['text'] = '%spark.pyspark' \
                   '\n'+df_name+'= load_df("(' + str(raw_query).replace("\n", " ") + ') AS SPARKQ0")' \
                   '\n'+df_name+'.printSchema()'
    data['editorHide'] = True
    # data['text'] =  '%spark.pyspark' \
    #                 '\n' + df_name + '= spark.read.format("jdbc")' \
    #                 '.option("url", "jdbc:postgresql://localhost:5432/bdo_platform?user=postgres&password=1234")' \
    #                 '.option("driver", "org.postgresql.Driver")' \
    #                 '.option("database", "bdo_platform")' \
    #                 '.option("dbtable", "(' + str(raw_query).replace("\n", " ") + ') AS SPARKQ0")' \
    #                 '.load()' \
    #                 '\n' + df_name + '.printSchema()'

    str_data = json.dumps(data)
    response = requests.post(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = response.json()
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def delete_zep_paragraph(notebook_id, paragraph_id):
    data = dict()
    str_data = json.dumps(data)
    response = requests.delete(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph/" + str(paragraph_id), data=str_data)
    print response


def delete_zep_notebook(notebook_id):
    data = dict()
    str_data = json.dumps(data)
    response = requests.delete(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id), data=str_data)
    print response


def execute_code_on_livy(code, session_id, kind):
    print 'executing code on livy'
    host = settings.LIVY_URL
    headers = {'Content-Type': 'application/json', 'X-Requested-By': 'Admin'}

    data = dict()
    data['code'] = code
    data['kind'] = kind
    statements_url = host + '/sessions/{0}/statements'.format(session_id)
    response = requests.post(statements_url, data=json.dumps(data), headers=headers).json()
    print response
    try:
        statement_id = response['id']
        state = ''
        from time import sleep
        sleep(3)  # Time in seconds.
        while state != 'available':
            r = requests.get(host + '/sessions/' + str(session_id) + '/statements/' + str(statement_id), headers=headers).json()
            # print json.dumps(r)
            state = r['state']
            if state == 'error' or state == 'cancelling' or state == 'cancelled':
                raise Exception('Failed')
            # print state
            if type(r) == dict and 'output' in r.keys():
                # print 'output in keys ' + str(r.keys())
                if type(r['output']) == dict and 'status' in r['output'].keys():
                    # print 'status in keys ' + str(r['output'].keys())
                    exec_status = r['output']['status']
                    if exec_status == 'error':
                        print 'Livy Execution Failed'
                        raise Exception('Livy Execution Failed')
    except Exception:
        raise Exception('Failed')
    return statement_id


def run_zep_paragraph(notebook_id, paragraph_id, livy_session_id, mode, attempt=2):
    if mode == 'livy':
        data = dict()
        str_data = json.dumps(data)
        response = requests.get(settings.ZEPPELIN_URL + "/api/notebook/" + str(notebook_id) + "/paragraph/" + str(paragraph_id), data=str_data)
        print response
        response_json = convert_unicode_json(response.json())
        code = str(response_json['body']['text']).strip().replace("u'{", "{")
        kind = 'spark'
        if 'pyspark' in code:
            kind = 'pyspark'
        code = code.replace('%spark.pyspark\n', '').replace('%spark.pyspark', '').replace('%pyspark\n', '').replace('%pyspark', '').replace('%spark\n', '').replace('%spark', '')

        if code is not None or code != '':
            execute_code_on_livy(code=code, session_id=livy_session_id, kind=kind)
        return 0 #end
    else:
        response_status = 500
        counter = 3
        while response_status != 200:
            data = dict()
            str_data = json.dumps(data)
            response = requests.post(settings.ZEPPELIN_URL+"/api/notebook/run/" + str(notebook_id) + "/" + str(paragraph_id), data=str_data)
            print response
            counter -= 1
            response_status = response.status_code
            if response_status != 200 and counter == 1:
                if attempt == 1:
                    import time
                    time.sleep(7)
                    restart_zep_interpreter(settings.ZEPPELIN_SPARK_INTERPRETER)
                    return 1
                else:
                    # return 2
                    return HttpResponse(status=500)
            if counter == 0:
                # return 2
                return HttpResponse(status=500)


def create_zep_viz_paragraph(notebook_id, title):
    data = dict()
    data['title'] = 'bdo_test_paragraph'
    data['text'] = '%sql' \
                   '\nselect * from tempTablePostgres'
    str_data = json.dumps(data)
    response = requests.post(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
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
    response = requests.post(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
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
    response = requests.post(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
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
    response = requests.put(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph/" + str(paragraph_id) + "/config", data=str_config)
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
    response = requests.put(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph/" + str(paragraph_id) + "/config", data=str_config)
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
    response = requests.put(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph/" + str(paragraph_id) + "/config", data=str_config)
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
    response = requests.put(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph/" + str(paragraph_id) + "/config", data=str_config)
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
    response = requests.put(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph/" + str(paragraph_id) + "/config", data=str_config)
    print response.json()


def restart_zep_interpreter(interpreter_id):
    print "RESTARTING INTERPRETER!!!"
    interpreter_id = 'settings.ZEPPELIN_SPARK_INTERPRETER'
    response = requests.put(settings.ZEPPELIN_URL+"/api/interpreter/setting/restart/"+interpreter_id)
    print response


def create_zep_drop_all_paragraph(notebook_id, title):
    data = dict()
    data['title'] = 'bdo_test_paragraph'
    data['text'] = '%spark.pyspark' \
                   '\nsqlContext.dropTempTable("tempTablePostgres")' \
                   '\ndf=None'

    str_data = json.dumps(data)
    response = requests.post(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = response.json()
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def create_zep_toJSON_paragraph(notebook_id, title, df_name, order_by='', order_type='ASC'):
    data = dict()
    data['title'] = 'bdo_test_paragraph'
    if order_by != '':
        if order_type == 'ASC':
            data['text'] = '%spark.pyspark' \
                           '\n{0}.orderBy("{1}", ascending=True).toJSON().collect()'.format(df_name, order_by)
        else:
            data['text'] = '%spark.pyspark' \
                           '\n{0}.orderBy("{1}", ascending=False).toJSON().collect()'.format(df_name, order_by)
    else:
        data['text'] = '%spark.pyspark' \
                       '\n{0}.toJSON().collect()'.format(df_name)

    str_data = json.dumps(data)
    response = requests.post(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = convert_unicode_json(response.json())
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def create_zep_tempView_paragraph(notebook_id, title, df_name):
    data = dict()
    data['title'] = 'bdo_test_paragraph'
    data['text'] = '%spark.pyspark' \
                   '\n{0}.createTempView("{0}_scala")'.format(df_name)

    str_data = json.dumps(data)
    response = requests.post(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = convert_unicode_json(response.json())
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def create_zep_scala_histogram_paragraph(notebook_id, title, df_name, hist_col, num_of_bins):
    data = dict()
    data['title'] = 'bdo_test_paragraph'
    data['text'] = '%spark' \
                   '\nval {0}_scala = spark.table("{0}_scala")' \
                   '\nval (startValues,counts) = {0}_scala.select("{1}").map(value => value.getDouble(0)).rdd.histogram({2})' \
                   '\nval {0}_scala = sc.parallelize(startValues zip counts).toDF("startValues","counts").withColumn("startValues", round($"startValues", 3))' \
                   '\nspark.sqlContext.dropTempTable("{0}_scala")'.format(df_name, hist_col, num_of_bins)

    str_data = json.dumps(data)
    response = requests.post(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = convert_unicode_json(response.json())
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def create_zep_scala_toJSON_paragraph(notebook_id, title, df_name):
    data = dict()
    data['title'] = 'bdo_test_paragraph'

    data['text'] = '%spark' \
                   '\n{0}_scala.orderBy("startValues").toJSON.collect'.format(df_name)


    str_data = json.dumps(data)
    response = requests.post(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = convert_unicode_json(response.json())
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def get_zep_scala_toJSON_paragraph_response(notebook_id, paragraph_id):
    print "request: "+settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph/"+str(paragraph_id)
    response = requests.get(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph/"+str(paragraph_id))
    print response
    response_json = convert_unicode_json(response.json())
    re = '[' + str(response_json['body']['results']['msg'][0]['data'].split('Array(')[1].split(')\n')[0]) + ']'
    json_data = json.loads(re)
    json_data = convert_unicode_json(json_data)
    return json_data


def get_zep_toJSON_paragraph_response(notebook_id, paragraph_id):
    print "request: "+settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph/"+str(paragraph_id)
    response = requests.get(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph/"+str(paragraph_id))
    print "get_zep_toJSON_paragraph_response:"
    print response
    # import pdb
    # pdb.set_trace()
    response_json = convert_unicode_json(response.json())
    json_data = json.loads(str(response_json['body']['results']['msg'][0]['data']).strip().replace("u'{", "{").replace("}'", "}").replace("'", '"'))
    print json_data[:3]
    print type(json_data)
    json_data = convert_unicode_json(json_data)
    print json_data[:3]
    # print type(json_data)

    return json_data


def create_zep_getDict_paragraph(notebook_id, title, dict_name):
    data = dict()
    data['title'] = 'bdo_test_paragraph'
    data['text'] = '%spark.pyspark' \
                   '\nprint {0}'.format(dict_name)

    str_data = json.dumps(data)
    response = requests.post(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph", data=str_data)
    print response
    response_json = convert_unicode_json(response.json())
    paragraph_id = response_json['body']
    print paragraph_id
    return paragraph_id


def get_zep_getDict_paragraph_response(notebook_id, paragraph_id):
    response = requests.get(settings.ZEPPELIN_URL+"/api/notebook/" + str(notebook_id) + "/paragraph/"+str(paragraph_id))
    print response
    response_json = convert_unicode_json(response.json())
    json_data = json.loads(str(response_json['body']['results']['msg'][0]['data']).strip().replace("u'{", "{").replace("}'", "}").replace("'", '"'))
    json_data = convert_unicode_json(json_data)
    return json_data


def create_livy_session(notebook_id):
    print 'looking for livy session'
    host = settings.LIVY_URL
    headers = {'Content-Type': 'application/json', 'X-Requested-By': 'Admin'}

    data = { 'kind': 'pyspark',
             'jars': ['/user/livy/jars/postgresql-42.2.2.jar', '/user/livy/jars/presto-jdbc-0.213.jar'],
             'driverMemory': '512m',
             'driverCores': 1,
             'numExecutors': 1,
             'executorMemory': '2g',
             'executorCores': 2,
             # 'heartbeatTimeoutInSecond': 120,
             'conf': {'spark.driver.maxResultSize': '2g'}}
    response = requests.post(host + '/sessions', data=json.dumps(data), headers=headers).json()
    # print response

    sessions = requests.get(host + '/sessions', headers=headers).json()['sessions']
    ids_states = [(int(s['id']),s['state'] ) for s in sessions]
    print 'session ids'
    print ids_states
    cnt=0
    session_id = -1
    print 'looking for session in list'
    for (id, state) in ids_states:
        cnt += 1
        if len(ServiceInstance.objects.filter(livy_session=id)) == 0:
            if state == 'starting' or state == 'idle':
                serviceInstance = ServiceInstance.objects.get(notebook_id=notebook_id)
                serviceInstance.livy_session = id
                serviceInstance.save()
                session_id = id
                break
    print 'found session?'
    print session_id

    if session_id == -1:
        try:
            response = requests.post(host + '/sessions', data=json.dumps(data), headers=headers).json()
            session_id = response['id']
        except Exception:
            raise Exception('Failed')
    try:
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
    headers = {'Content-Type': 'application/json', 'X-Requested-By': 'Admin'}
    raw_query = '(SELECT * FROM (SELECT * from wind_speed_11) AS SQ1 LIMIT 1000000) AS tmp'
    data = dict()
    data['code'] = 'df = spark.read.format("jdbc")' \
                   '.option("url", "jdbc:postgresql://localhost:5432/bdo_platform?user=postgres&password=bdo!")' \
                   '.option("driver", "org.postgresql.Driver")' \
                   '.option("database", "bdo_platform")' \
                   '.option("dbtable", "' + str(raw_query).replace("\n", " ") + '")' \
                   '.load()' \
                   '\n#df.show()'

    statements_url = host + '/sessions/{0}/statements'.format(session_id)
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


def create_livy_toJSON_paragraph(session_id, df_name, order_by='', order_type='ASC'):
    host = settings.LIVY_URL
    headers = {'Content-Type': 'application/json', 'X-Requested-By': 'Admin'}

    data = dict()
    if order_by != '':
        if order_type == 'ASC':
            data['code'] = '{0}.orderBy("{1}", ascending=True).toJSON().collect()'.format(df_name, order_by)
        else:
            data['code'] = '{0}.orderBy("{1}", ascending=False).toJSON().collect()'.format(df_name, order_by)
    else:
        data['code'] = '{0}.toJSON().collect()'.format(df_name)

    statements_url = host + '/sessions/{0}/statements'.format(session_id)
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
    # return_val = ast.literal_eval(response['output']['data']['text/plain'])
    # print return_val
    # return return_val
    return json.loads(response['output']['data']['text/plain'].replace("\'","'").replace("u'{", "{").replace("}',", "},").replace("}']", "}]").replace("'", '"'))


def create_livy_scala_toJSON_paragraph(session_id, df_name):
    host = settings.LIVY_URL
    headers = {'Content-Type': 'application/json', 'X-Requested-By': 'Admin'}

    data = dict()
    data['code'] = '{0}_scala.orderBy("startValues").toJSON.collect'.format(df_name)
    data['kind'] = 'spark'
    statements_url = host + '/sessions/{0}/statements'.format(session_id)
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
    return_val = '[' + str(convert_unicode_json(response['output']['data']['text/plain'].replace("u'{", "{").replace("}',", "},").replace("}']", "}]").replace("'", '"').split('Array(')[1].replace('})', '}').replace('\n', ''))) + ']'
    return json.loads(return_val)


def get_result_dict_from_livy(session_id, dict_name):
    host = settings.LIVY_URL
    headers = {'Content-Type': 'application/json', 'X-Requested-By': 'Admin'}

    data = dict()
    data['code'] = '\nprint {0}'.format(dict_name)
    data['kind'] = 'pyspark'

    statements_url = host + '/sessions/{0}/statements'.format(session_id)
    response = requests.post(statements_url, data=json.dumps(data), headers=headers).json()
    print response
    try:
        statement_id = response['id']
        state = ''
        from time import sleep
        sleep(3)  # Time in seconds.
        while state != 'available':
            response = requests.get(host + '/sessions/' + str(session_id) + '/statements/' + str(statement_id), headers=headers).json()
            state = response['state']
            if state == 'error' or state == 'cancelling' or state == 'cancelled':
                raise Exception('Failed')
    except Exception:
        raise Exception('Failed')
    print 'result'
    print str(response['output']['data'])
    # return_val = json.loads(str(convert_unicode_json(response['output']['data']['text/plain'])).replace("'", '"'))
    return_val = ast.literal_eval(response['output']['data']['text/plain'])
    print return_val
    return return_val


def close_livy_session(session_id):
    headers = {'X-Requested-By': 'Admin'}
    requests.delete("{0}/sessions/{1}".format(settings.LIVY_URL, session_id), headers=headers)
