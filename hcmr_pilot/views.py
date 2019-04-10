import csv
import json

import requests
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
import time
from pandas import DataFrame
from .forms import HCMRForm
import calculate_red_points as red_points_calc
from django.conf import settings
from service_builder.models import Service, ServiceInstance
from threading import Thread
from datetime import datetime


def init(request):
    form = HCMRForm()
    scenario = request.GET['scenario']
    print scenario

    execution_steps = dict()
    execution_steps['OIL_SPILL_SCENARIO_1'] = ["starting service", "Creating simulation request",
                                               "Simulation running", "Simulation results received",
                                               "Transforming data to be shown on map",
                                               "Calculating oil spill intersections with protected areas", "done"]
    execution_steps['OIL_SPILL_SCENARIO_2'] = ["starting service", "Creating simulation request",
                                               "Simulation running", "Simulation results received",
                                               "Transforming data to be shown on map",
                                               "Calculating oil spill intersections with protected areas", "done"]
    execution_steps['OIL_SPILL_SCENARIO_3'] = ["starting service", "Creating simulation request",
                                               "Simulation running", "Simulation results received",
                                               "Transforming data to be shown on map",
                                               "Calculating oil spill intersections with protected areas", "done"]
    list = []
    for i in range(0, 61):
        list.append(i*12)
    return render(request, 'hcmr_pilot/load_service.html', {'form': form, 'scenario': scenario, 'execution_steps': execution_steps, 'sim_len_list': list})


def scenario1_results(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    visualization_url = service_exec.dataframe_visualizations['v1']
    filename_output = service_exec.arguments['algorithm-arguments'][0]['out_filepath']
    location_lat = float(service_exec.arguments['algorithm-arguments'][0]['latitude'])
    location_lon = float(service_exec.arguments['algorithm-arguments'][0]['longitude'])
    start_date = service_exec.arguments['algorithm-arguments'][0]['start_date']
    oil_volume = service_exec.arguments['algorithm-arguments'][0]['oil_volume']
    wave_forecast_dataset = service_exec.arguments['algorithm-arguments'][0]['wave_model']
    hydrodynamic_model = service_exec.arguments['algorithm-arguments'][0]['ocean_model']
    import time
    from datetime import datetime

    spill_data = service_exec.arguments['algorithm-arguments'][1]['spill_data']
    headers_spill = service_exec.arguments['algorithm-arguments'][1]['headers_spill']
    legend_data = [{"timestamp": long(time.mktime(datetime.strptime(d[0], "%Y-%m-%d %H:%M:%S").timetuple()) * 1000),
                    "time": d[0], "init_vol": oil_volume,  "evap_vol": d[2],  "emul_vol": d[4],
                    "vol_on_surface": d[3],  "vol_on_coasts": d[6], } for d in spill_data]

    context = {
        'url': visualization_url,
        'out_filepath': filename_output,
        'legend_data': legend_data,
        'result': [],
        'service_title': 'Oil Spill Dispersion in the Marine Environment',
        'back_url': '/oilspill/?scenario=1',
        'study_conditions': [{'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):', 'value': '(' + str(round(location_lat, 3)) + ', ' + str(round(location_lon,3)) + ')'},
                             {'icon': 'far fa-calendar-alt', 'text': 'Time:', 'value': str(start_date)},
                             {'icon': 'fas fa-flask', 'text': 'Oil Volume:', 'value': str(oil_volume) + ' m3'},
                             {'icon': 'fas fa-database', 'text': 'Wave Forecast Dataset:', 'value': str(wave_forecast_dataset)},
                             {'icon': 'fas fa-box', 'text': 'Hydrodynamic Model:', 'value': str(hydrodynamic_model)}],
    }
    return render(request, 'hcmr_pilot/scenario1-results.html', context)


def scenario2_results(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    visualization_url = service_exec.dataframe_visualizations['v1']
    filename_output = service_exec.arguments['algorithm-arguments'][0]['out_filepath']
    list_of_points = []
    alg_arguments = service_exec.arguments['algorithm-arguments'][0]
    # import pdb
    # pdb.set_trace()
    for i in range(1, alg_arguments['number_of_points']+1):
        list_of_points.append((round(float(alg_arguments['latitude' + str(i)]), 3), (round(float(alg_arguments['longitude' + str(i)]), 3))))
    start_date = service_exec.arguments['algorithm-arguments'][0]['start_date']
    oil_volume = service_exec.arguments['algorithm-arguments'][0]['oil_volume']
    wave_forecast_dataset = service_exec.arguments['algorithm-arguments'][0]['wave_model']
    hydrodynamic_model = service_exec.arguments['algorithm-arguments'][0]['ocean_model']
    import time
    from datetime import datetime

    spill_data = service_exec.arguments['algorithm-arguments'][1]['spill_data']
    headers_spill = service_exec.arguments['algorithm-arguments'][1]['headers_spill']
    legend_data = [{"timestamp": long(time.mktime(datetime.strptime(d[0], "%Y-%m-%d %H:%M:%S").timetuple()) * 1000),
                    "time": d[0], "init_vol": oil_volume, "evap_vol": d[2], "emul_vol": d[4],
                    "vol_on_surface": d[3], "vol_on_coasts": d[6], } for d in spill_data]

    context = {
        'url': visualization_url,
        'out_filepath': filename_output,
        'legend_data': legend_data,
        'result': [],
        'service_title': 'Oil Spill Dispersion in the Marine Environment',
        'back_url': '/oilspill/?scenario=2',
        'study_conditions': [{'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):',
                              'value': str(list_of_points)},
                             {'icon': 'far fa-calendar-alt', 'text': 'Time:', 'value': str(start_date)},
                             {'icon': 'fas fa-flask', 'text': 'Oil Volume:', 'value': str(oil_volume) + ' m3'},
                             {'icon': 'fas fa-database', 'text': 'Wave Forecast Dataset:',
                              'value': str(wave_forecast_dataset)},
                             {'icon': 'fas fa-box', 'text': 'Hydrodynamic Model:', 'value': str(hydrodynamic_model)}],
    }
    return render(request, 'hcmr_pilot/scenario1-results.html', context)


def scenario3_results(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    visualization_url = service_exec.dataframe_visualizations['v1']
    filename_output = service_exec.arguments['algorithm-arguments'][0]['out_filepath']
    location_lat = float(service_exec.arguments['algorithm-arguments'][0]['latitude'])
    location_lon = float(service_exec.arguments['algorithm-arguments'][0]['longitude'])
    start_date = service_exec.arguments['algorithm-arguments'][0]['start_date']
    oil_volume = service_exec.arguments['algorithm-arguments'][0]['oil_volume']
    wave_forecast_dataset = service_exec.arguments['algorithm-arguments'][0]['wave_model']
    hydrodynamic_model = service_exec.arguments['algorithm-arguments'][0]['ocean_model']
    import time
    from datetime import datetime

    spill_data = service_exec.arguments['algorithm-arguments'][1]['spill_data']
    headers_spill = service_exec.arguments['algorithm-arguments'][1]['headers_spill']
    legend_data = [{"timestamp": long(time.mktime(datetime.strptime(d[0], "%Y-%m-%d %H:%M:%S").timetuple()) * 1000),
                    "time": d[0], "init_vol": oil_volume, "evap_vol": d[2], "emul_vol": d[4],
                    "vol_on_surface": d[3], "vol_on_coasts": d[6], } for d in spill_data]

    output_json = filename_output.replace('_F.out', '.json')
    # rp_file = filename_output.replace('_F.out', '.txt')
    # red_points = get_red_points(rp_file)

    depth_data = extract_depth_data(str(output_json))
    context = {
        'depth_data': depth_data,
        'url': visualization_url,
        'out_filepath': filename_output,
        'legend_data': legend_data,
        'result': [],
        'service_title': 'Oil Spill Dispersion in the Marine Environment',
        'back_url': '/oilspill/?scenario=1',
        'study_conditions': [{'icon': 'fas fa-map-marker-alt', 'text': 'Location (latitude, longitude):',
                              'value': '(' + str(round(location_lat, 3)) + ', ' + str(round(location_lon, 3)) + ')'},
                             {'icon': 'far fa-calendar-alt', 'text': 'Time:', 'value': str(start_date)},
                             {'icon': 'fas fa-flask', 'text': 'Oil Volume:', 'value': str(oil_volume) + ' m3'},
                             {'icon': 'fas fa-database', 'text': 'Wave Forecast Dataset:',
                              'value': str(wave_forecast_dataset)},
                             {'icon': 'fas fa-box', 'text': 'Hydrodynamic Model:', 'value': str(hydrodynamic_model)}],
    }
    return render(request, 'hcmr_pilot/scenario3-results.html', context)


def index(request):
    if request.method == 'GET':
        form = HCMRForm(request.GET)
        if form.is_valid():
            return HttpResponseRedirect('/process/')
    else:
        form = HCMRForm()
    return render(request, 'hcmr_pilot/config-service-form-fields.html', {'form': form})


def execute(request):
    service = Service.objects.get(pk=settings.OIL_SPILL_SERVICE_ID)
    service_exec = ServiceInstance(service=service, user=request.user, time=datetime.now(),
                                   status="starting service", dataframe_visualizations=[])
    service_exec.save()
    # Spawn thread to process the data
    t = Thread(target=process, args=(request, service_exec.id))
    t.start()
    return JsonResponse({'exec_instance': service_exec.id})


def process(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    try:
        service_exec.arguments = {"filter-arguments": [], "algorithm-arguments": [{}, {}]}

        spill_infos, wave_model, ocean_model, natura_layer, ais_layer, time_interval, sim_length, oil_density, valid_points, valid_points_count, scenario, depth = parse_request_params(request)
        if (scenario == '1') or (scenario == '3'):
            service_exec.arguments["algorithm-arguments"][0]["latitude"] = spill_infos[0]['latitude']
            service_exec.arguments["algorithm-arguments"][0]["longitude"] = spill_infos[0]['longitude']
            if scenario == '3':
                service_exec.arguments["algorithm-arguments"][0]["depth"] = spill_infos[0]['depth']

        elif scenario == '2':
            count = 1
            for el in spill_infos:
                service_exec.arguments["algorithm-arguments"][0]["latitude"+str(count)] = spill_infos[count-1]['latitude']
                service_exec.arguments["algorithm-arguments"][0]["longitude"+str(count)] = spill_infos[count-1]['longitude']
                count = count + 1
            service_exec.arguments["algorithm-arguments"][0]["number_of_points"] = count - 1

        service_exec.arguments["algorithm-arguments"][0]["start_date"] = spill_infos[0]['start_date']
        service_exec.arguments["algorithm-arguments"][0]["oil_volume"] = spill_infos[0]['oil_volume']
        if wave_model == '202':
            service_exec.arguments["algorithm-arguments"][0]["wave_model"] = 'Poseidon Wave Dataset for the Aegean'
        elif wave_model == '201':
            service_exec.arguments["algorithm-arguments"][0]["wave_model"] = 'Poseidon Wave Dataset for the Mediterranean'
        elif wave_model == '203':
            service_exec.arguments["algorithm-arguments"][0]["wave_model"] = 'Copernicus Wave Dataset'
        else:
            service_exec.arguments["algorithm-arguments"][0]["wave_model"] = ''

        if ocean_model == '001':
            service_exec.arguments["algorithm-arguments"][0]["ocean_model"] = 'Poseidon High Resolution Aegean Model'
        elif ocean_model == '002':
            service_exec.arguments["algorithm-arguments"][0]["ocean_model"] = 'Poseidon Mediterranean Model'
        elif ocean_model == '003':
            service_exec.arguments["algorithm-arguments"][0]["ocean_model"] = 'Copernicus Model'
        else:
            service_exec.arguments["algorithm-arguments"][0]["ocean_model"] = ''

        service_exec.arguments["algorithm-arguments"][0]["natura_layer"] = natura_layer
        service_exec.arguments["algorithm-arguments"][0]["ais_layer"] = ais_layer

        # 1)Create input file
        if service_exec.status == 'failed':
            raise Exception
        service_exec.status = "Creating simulation request"
        service_exec.save()
        filename, url_params = create_inp_file_from_request_and_upload(request)
        # 2)Calculate oil spill
        if service_exec.status == 'failed':
            raise Exception
        service_exec.status = "Simulation running"
        service_exec.save()
        found = wait_until_output_ready(url_params, request)
        if found:
            if service_exec.status == 'failed':
                raise Exception
            service_exec.status = "Simulation results received"
            service_exec.save()
            filename_output = str(filename).replace("_F.inp", "_F.out")
            hcmr_data_filename = str(filename).replace("_F.inp", ".json")
            red_points_filename = str(filename).replace("_F.inp", ".txt")

            # 3)Transforming data to be shown on map
            if service_exec.status == 'failed':
                raise Exception
            service_exec.status = "Transforming data to be shown on map"
            service_exec.save()
            output_path = 'service_builder/static/services_files/hcmr_service_1/' + filename_output
            spill_data, parcel_data = create_json_from_out_file(output_path)
            # spill_data = [spill_infos[0]['start_date']+':00', spill_infos[0]['latitude'], spill_infos[0]['longitude'], spill_data[0][3], spill_data[0][4], spill_data[0][3], spill_infos[0]['oil_volume'],spill_data[0][5], spill_data[0][6]]
            print str(spill_infos[0]['latitude'])+ ' ' + spill_infos[0]['longitude']
            print str(valid_points[0][0]) + ' ' + str(valid_points[0][1])
            for el in valid_points:
                parcel_data.insert(0,[spill_infos[0]['start_date'].encode('ascii') + ':00', float(el[0]),float(el[1]),
                              parcel_data[0][3], parcel_data[0][4], float(spill_infos[0]['oil_volume']),
                              parcel_data[0][6], parcel_data[0][7]])
            spill_data.insert(0,
                               [spill_infos[0]['start_date'].encode('ascii') + ':00', spill_data[0][1], spill_data[0][2], spill_data[0][3], spill_data[0][4], spill_data[0][5], spill_data[0][6], spill_data[0][7], spill_data[0][8], spill_data[0][9], spill_data[0][10]])

            print 'create_json_from_out_file done'
            headers_parcel = ["time", "Lat", "Lon", "Dpth", "Status", "Volume(m3)", "Dens", "Visc"]
            parcel_df = DataFrame(parcel_data, columns=headers_parcel)
            print 'parcel_df = DataFrame done'
            print(parcel_df.head(2))
            parcel_df.to_json('visualizer/static/visualizer/files/'+ hcmr_data_filename, orient = 'records')
            print 'parcel_df.to_json done'

            headers_spill = ['time', 'N', '%ev', '%srf', '%em', '%disp', '%cst', '%btm', 'max_visc', 'min_visc', 'dens']
            service_exec.arguments["algorithm-arguments"][1]["headers_spill"] = headers_spill
            service_exec.arguments["algorithm-arguments"][1]["spill_data"] = spill_data
            service_exec.save()

            print 'spill_data done'

            # 4)Calculate red points
            if service_exec.status == 'failed':
                raise Exception
            service_exec.status = "Calculating oil spill intersections with protected areas"
            service_exec.save()
            if natura_layer == "true":
                # red_points_calc.calculate(hcmr_data_filename, red_points_filename)
                pass

            print 'red points calculated'
            # 5)Create Visualization
            visualization_url = "http://" + request.META[
                'HTTP_HOST'] + "/visualizations/map_markers_in_time_hcmr/" + "?markerType=circle&lat_col=Lat&lon_col=Lon" + "&data_file=" + hcmr_data_filename + "&red_points_file=" + red_points_filename + "&natura_layer=" + natura_layer + "&ais_layer=" + ais_layer + "&time_interval=" + time_interval

            service_exec.dataframe_visualizations = {"v1": visualization_url}
            service_exec.arguments["algorithm-arguments"][0]["out_filepath"] = filename_output
            if service_exec.status == 'failed':
                raise Exception
            service_exec.status = "done"
            service_exec.save()

            # context = {
            #     'url': visualization_url,
            #     'out_filepath': filename_output,
            # }
            # return render(request, 'hcmr_pilot/scenario1-results.html', context)
        else:
            # html = "<html><body>Something went wrong. Please, try again.</body></html>"
            # return HttpResponse(html)
            service_exec.status = "failed"
            service_exec.save()
    except:
        service_exec.status = "failed"
        service_exec.save()


def status(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    return JsonResponse({'status': service_exec.status})


def create_json_from_out_file(filename_output):
    from datetime import datetime, timedelta
    with open(filename_output, "r") as f:
        parcel_data = []
        spill_data = []
        f.readline()
        f.readline()
        f.readline()
        f.readline()
        line = f.readline()
        print line
        start_datetime = datetime.strptime(line.strip(), '%Y %m %d %H%M')
        print start_datetime
        while line.strip() != "*** End of Input ***":
            if len(line) == 0:
                return spill_data, parcel_data
            line = f.readline()
        print line
        first_line = f.readline()
        while first_line.strip() != '':
            while is_integer_string(f.readline().split()[0]):
                pass
            time, n, ev, srf, em, disp, cst, btm, max_visc, min_visc, dens = f.readline().split()
            datetime = start_datetime + timedelta(hours=float(time))
            spill_data.append(
                [str(datetime), int(n), float(ev), float(srf), float(em), float(disp), float(cst), float(btm),
                 float(max_visc), float(min_visc), float(dens)])
            f.readline()
            for i in range(0, int(n)):
                lat, lon, dpth, status, volume, dens, visc = f.readline().split()
                parcel_data.append(
                    [str(datetime), float(lat), float(lon), float(dpth), int(status), float(volume), float(dens),
                     float(visc)])
            first_line = f.readline()
        f.close()
    print parcel_data[-1]
    return spill_data, parcel_data


def wait_until_output_ready(params, request):
    found = False
    error = False
    tries = 40
    while (not found) and (tries > 0) and (not error):
        tries -= 1
        time.sleep(8)
        response = requests.get("http://" + request.META['HTTP_HOST'] + "/service_builder/api/checkIfOutputExistsforHCMRSpillSimulator/?" + params)
        print(response)
        print "<status>" + str(response.status_code) + "</status>"
        if int(response.status_code) == 200:
            return True
        elif int(response.status_code) == 300:
            continue
        else:
            return False


def create_inp_file_from_request_and_upload(request):
    spill_infos, wave_model, ocean_model, natura_layer, ais_layer, time_interval, sim_length, oil_density, valid_points, valid_points_count,scenario, depth = parse_request_params(request)
    url_params = build_request_params_for_file_creation(spill_infos, wave_model, ocean_model, oil_density, sim_length, time_interval,depth)
    response = requests.get("http://" + request.META['HTTP_HOST'] + "/service_builder/api/createInputFileForHCMRSpillSimulator/?" + url_params)
    print "<status>" + str(response.status_code) + "</status>"
    filename = ''
    if int(response.status_code) == 200:
        filename = str(response.json()['filename'])
        print filename
    return filename, url_params


def build_request_params_for_file_creation(spill_info_list, wave_model, ocean_model, oil_density, sim_length, time_interval, depth):
    url_params = ''
    idx = 0
    for point in spill_info_list:
        start_date = point['start_date']
        latitude = point['latitude']
        longitude = point['longitude']
        oil_volume = point['oil_volume']
        date, daytime = start_date.split(' ')
        print(date)
        year, month, day = date.split('-')
        hours, mins = daytime.split(':')
        if idx == 0 :
            url_params += "LATLON" + str(idx) + "=" + str(latitude) + '%20' + str(longitude)
        else :
            url_params += "&LATLON"+str(idx)+ "=" + str(latitude) + '%20' + str(longitude)
        url_params += "&DATETIME"+str(idx)+"=" + year + '%20' + month + '%20' + day+'+'+hours+mins
        url_params += "&VOLUME"+str(idx)+"=" + str(oil_volume)
        idx += 1
    url_params += '&WAVE_MODEL='+str(wave_model)
    url_params += '&OCEAN_MODEL='+ str(ocean_model)
    url_params += '&DENSITYOILTYPE=' + str(oil_density)
    url_params += '&SIM_LENGTH=' + str(sim_length)
    url_params += '&DENSITYOILTYPE=' + str(oil_density)
    url_params += '&STEP=' + str(time_interval)
    url_params += '&DEPTH0=' + str(depth)

    return url_params


def parse_request_params(request):
    spill_infos = []
    valid_points_count = 0
    valid_points = []
    scenario = str(request.GET.get('scenario'))
    for i in range(1,6):
        spill_info = {}
        spill_info['latitude'] = latitude = request.GET.get('latitude'+str(i))
        spill_info['longitude'] = longitude = request.GET.get('longitude'+str(i))
        spill_info['start_date'] = start_date = request.GET.get('start_date'+str(i))
        spill_info['oil_volume'] = oil_volume = request.GET.get('oil_volume'+str(i))
        print (latitude, longitude, start_date, oil_volume)
        if (latitude == '' or latitude == 'undefined' or longitude == '' or longitude == 'undefined' or start_date == '' or start_date == 'undefined' or oil_volume == '' or oil_volume == 'undefined' ):
            break
        else:
            spill_infos.append(spill_info)
            valid_points_count = valid_points_count + 1
            valid_points.append([spill_info['latitude'], spill_info['longitude']])
        print(spill_infos)
    if scenario == '3':
        spill_infos[0]['depth'] = request.GET.get('depth')
    wave_model = request.GET.get('wave_model')
    ocean_model = request.GET.get('hd_model')
    natura_layer = request.GET.get('natura_layer')
    ais_layer = request.GET.get('ais_layer')
    time_interval = request.GET.get('time_interval')
    sim_length = request.GET.get('simulation_length')
    oil_density = request.GET.get('oil_density')
    depth = request.GET.get('depth')
    return spill_infos, wave_model, ocean_model, natura_layer, ais_layer, time_interval, sim_length, oil_density, valid_points, valid_points_count,scenario, depth


def is_integer_string(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def download(request):
    out = request.GET.get('file')
    content = open('service_builder/static/services_files/hcmr_service_1/'+out).read()
    print(content)
    response = HttpResponse(content, content_type='text/plain')
    return response


def create_map_grid_for_natura(request):
    from shapely.geometry import Polygon
    from shapely.geometry import Point
    import csv
    import time
    ts = time.time()
    natura_grid_file_name = str(request.GET.get('natura_file_name', ''))+str(ts).replace('.','')
    kml_filepath = 'visualizer/static/visualizer/files/kml2.json'
    with open(kml_filepath) as json_kml_data:
        kml_data = json.load(json_kml_data)
    file = open('visualizer/static/visualizer/files/' + natura_grid_file_name, 'w')
    # resolution in the form of a multiplier
    multiplier = 1000
    # max,min lat/lons of the area to be separated into a grid
    max_lat = 40.000000
    min_lat = 34.808124
    max_lon = 28.495422
    min_lon = 21.750412
    lat_dist = max_lat - min_lat
    lon_dist = max_lon - min_lon
    polygons = []
    for kd in kml_data['placemarks']:
        for point in kd['polygons']:
            polygon = {}
            outer_p = []
            o = point['outer_boundary']
            for c in o['coordinates']:
                outer_p.append((c['latitude'], c['longitude']))
            inner_polygons = []
            for i in point['inner_boundaries']:
                inner_p = []
                for c in i['coordinates']:
                    inner_p.append((c['latitude'], c['longitude']))
                inner_polygons.append(inner_p)
            polygon['outer'] = outer_p
            polygon['inners'] = inner_polygons
            polygon['min_lat'] = point['outer_boundary']['min_lat']
            polygon['max_lat'] = point['outer_boundary']['max_lat']
            polygon['min_lon'] = point['outer_boundary']['min_lon']
            polygon['max_lon'] = point['outer_boundary']['max_lon']
            polygons.append(polygon)
    natura_grid = []
    lat_max = int(lat_dist*multiplier)
    lon_max = int(lon_dist*multiplier)
    for lat in range(0, lat_max):
        natura_grid_row = []
        for lon in range(0, lon_max):
            # clearing irrelevant natura polygons
            cleared_polygons = []
            for po in polygons:
                po_min_lat = float(po['min_lat'])
                po_max_lat = float(po['max_lat'])
                po_min_lon = float(po['min_lon'])
                po_max_lon = float(po['max_lon'])
                checked_point_lat = (float(lat)/multiplier + min_lat)
                checked_point_lon = (float(lon)/multiplier + min_lon)
                if checked_point_lat > po_max_lat or checked_point_lat < po_min_lat or checked_point_lon > po_max_lon or checked_point_lon < po_min_lon:
                    continue
                cleared_polygons.append(po)

            print 'checking point:('+str(float(lat)/multiplier + min_lat)+','+str(float(lon)/multiplier + min_lon)+')'
            is_inner = False
            found_natura = False
            for pol in cleared_polygons:
                inner_pols = pol['inners']
                if is_inner:
                    break
                for in_pol in inner_pols:
                    shapely_pol = Polygon(in_pol)
                    if is_inner:
                        break
                    if shapely_pol.contains(Point((float(lat)/multiplier + min_lat), (float(lon)/multiplier + min_lon))):
                        is_inner = True
                outer_pol = pol['outer']
                shapely_pol = Polygon(outer_pol)
                if shapely_pol.contains(Point((float(lat)/multiplier + min_lat), (float(lon)/multiplier + min_lon))):
                    found_natura = True
                    break
            if found_natura:
                natura_grid_row.append(1)
            else:
                natura_grid_row.append(0)
        natura_grid.append(natura_grid_row)
    file.close()
    dic = {}
    with open('visualizer/static/visualizer/files/natura_grid_fr.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        [writer.writerow(r) for r in natura_grid]
        csvfile.close()
    with open('visualizer/static/visualizer/files/natura_grid_info_fr', 'w') as file:
        dic['resolution'] = multiplier
        dic['min_lat'] = min_lat
        dic['min_lon'] = min_lon
        json.dump(dic, file, default=myconverter)

    return JsonResponse({'status': "completed"})

def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()


def cancel_execution(request, exec_instance):
    print "Cancelling"
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    service_exec.status = "failed"
    service_exec.save()
    print "Cancelled?"
    return JsonResponse({'status': "cancelled"})


def extract_depth_data(json_data_file):
    with open('visualizer/static/visualizer/files/' + json_data_file) as json_file:
        data = json.load(json_file)
        points = []
        natura_table, resolution, min_lat, min_lon = get_natura_table()
        for p in data:
            lat, lon = p['Lat'],p['Lon']
            status = p['Status']
            point = {"depth": p['Dpth'],
                     "lat": lat,
                     "lon": lon,
                     "time": p["time"],
                     "color": get_color(natura_table, lat, lon, status, resolution, min_lat, min_lon)}
            points.append(point)
        return points


def get_natura_table():
    with open('visualizer/static/visualizer/files/natura_grid_fr.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        natura_table = [[int(e) for e in r] for r in reader]
        csvfile.close()
    with open('visualizer/static/visualizer/files/natura_grid_info_fr', 'r') as file:
        natura_info = json.load(file)
    min_grid_lat = natura_info['min_lat']
    min_grid_lon = natura_info['min_lon']
    resolution = natura_info['resolution']
    return natura_table, resolution, min_grid_lat, min_grid_lon


def get_color(natura_table, lat, lon, status, resolution, min_lat, min_lon):
    if len(natura_table) != 0:
        try:
            x = int((lat - min_lat)*resolution)
            y = int((lon - min_lon)*resolution)
            if (x>0) and (y>0):
                if natura_table[x][y] == 1:
                    return 'red'
            else:
                pass
        except:
            pass
    if status == 0:
        return 'darkblue'
    elif status == 1:
        return 'lightblue'
    elif status == 5:
        return 'cadetblue'
    elif status == 10:
        return 'orange'
    else:
        return 'lightblue'
