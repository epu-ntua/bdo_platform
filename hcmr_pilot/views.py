import requests
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
import time
from pandas import DataFrame
from .forms import HCMRForm
import calculate_red_points as red_points_calc


def init(request):
    form = HCMRForm()
    return render(request, 'hcmr_pilot/load_service.html', {'form': form})


def results(request):

    return render(request, 'hcmr_pilot/oilspill-results.html')


def index(request):
    if request.method == 'GET':
        form = HCMRForm(request.GET)
        if form.is_valid():
            return HttpResponseRedirect('/process/')
    else:
        form = HCMRForm()
    return render(request, 'hcmr_pilot/config-service-form-fields.html', {'form': form})


def process(request):
    # 1)Create input file
    filename, url_params = create_inp_file_from_request_and_upload(request)
    # 2)Calculate oil spill
    wait_until_output_ready(url_params)
    filename_output = str(filename).replace("_F.inp", "_F.out")
    hcmr_data_filename = str(filename).replace("_F.inp", ".json")
    red_points_filename = str(filename).replace("_F.inp", ".txt")

    # 3)Transform data to show in map
    spill_data, parcel_data = create_json_from_out_file(
        'service_builder/static/services_files/hcmr_service_1/' + filename_output)

    headers_parcel = ["time", "Lat", "Lon", "Dpth", "Status", "Volume(m3)", "Dens", "Visc"]
    parcel_df = DataFrame(parcel_data, columns = headers_parcel)

    print(parcel_df.head(10))
    parcel_df.to_json('visualizer/static/visualizer/files/'+ hcmr_data_filename, orient = 'records')

    # 4)Calculate red points
    red_points_calc.calculate(hcmr_data_filename, red_points_filename)

    # 5)Create Visualization
    visualization_url = "http://localhost:8000/visualizations/map_markers_in_time_hcmr/" + "?notebook_id=2DX2PVRRQ&df=parcel_data_df&markerType=circle&lat_col=Lat&lon_col=Lon" + "&data_file=" + hcmr_data_filename + "&red_points_file=" + red_points_filename
    context = {
        'url': visualization_url,
    }
    return render(request, 'hcmr_pilot/oilspill-results.html', context)



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


def wait_until_output_ready(params):
    found = False
    error = False
    tries = 12
    while (not found) and (tries > 0) and (not error):
        tries -= 1
        time.sleep(2)
        response = requests.get(
            "http://localhost:8000/service_builder/api/checkIfOutputExistsforHCMRSpillSimulator/?"+params)
        print(response)
        print "<status>" + str(response.status_code) + "</status>"
        if int(response.status_code) == 200:
            return
        elif int(response.status_code) == 300:
            continue
        else:
            return


def create_inp_file_from_request_and_upload(request):
    spill_infos = parse_request_params(request)
    url_params = build_request_params_for_file_creation(spill_infos)
    response = requests.get(
        "http://localhost:8000/service_builder/api/createInputFileForHCMRSpillSimulator/?" + url_params)
    print "<status>" + str(response.status_code) + "</status>"
    filename = ''
    if int(response.status_code) == 200:
        filename = str(response.json()['filename'])
        print filename
    return filename, url_params


def build_request_params_for_file_creation(spill_info_list):
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

    return url_params


def parse_request_params(request):
    spill_infos = []
    for i in range(1,6):
        spill_info = {}
        spill_info['latitude'] = latitude = request.GET.get('latitude'+str(i))
        spill_info['longitude'] = longitude = request.GET.get('longitude'+str(i))
        spill_info['start_date'] = start_date = request.GET.get('start_date'+str(i))
        spill_info['oil_volume'] = oil_volume = request.GET.get('oil_volume'+str(i))
        print (latitude,longitude, start_date, oil_volume)
        if (latitude == '' or longitude == '' or start_date == '' or oil_volume == ''):
            break
        else:
            spill_infos.append(spill_info)
        print(spill_infos)
    return spill_infos


def is_integer_string(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
