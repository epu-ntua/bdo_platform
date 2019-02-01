import requests
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
import time
from pandas import DataFrame
from .forms import HCMRForm
import calculate_red_points as red_points_calc


def index(request):
    if request.method == 'GET':
        form = HCMRForm(request.GET)
        if form.is_valid():
            return HttpResponseRedirect('/process/')
    else:
        form = HCMRForm()
    return render(request, 'hcmr_pilot/config-service-form-fields.html', {'form': form})


def process(request):
    filename, url_params = create_inp_file_from_request_and_upload(request)
    wait_until_output_ready(url_params)
    filename_output = str(filename).replace("_F.inp", "_F.out")
    hcmr_data_filename = str(filename).replace("_F.inp", ".json")
    red_points_filename = str(filename).replace("_F.inp", ".txt")
    spill_data, parcel_data = create_json_from_out_file(
        'service_builder/static/services_files/hcmr_service_1/' + filename_output)

    headers_parcel = ["time", "Lat", "Lon", "Dpth", "Status", "Volume(m3)", "Dens", "Visc"]
    parcel_df = DataFrame(parcel_data, columns = headers_parcel)
    # headers_spill = ["time", "N", "ev", "srf", "em", "disp", "cst", "btm", "max_visc", "min_visc", "dens"]
    # spill_df = DataFrame(spill_data, columns=headers_spill)
    print(parcel_df.head(10))
    parcel_df.to_json('visualizer/static/visualizer/files/'+ hcmr_data_filename, orient = 'records')
    red_points_calc.calculate(hcmr_data_filename, red_points_filename)
    return redirect("http://localhost:8000/visualizations/map_markers_in_time_hcmr/"
                    + "?notebook_id=2DX2PVRRQ&df=parcel_data_df&markerType=circle&lat_col=Lat&lon_col=Lon"
                    + "&data_file="+hcmr_data_filename+"&red_points_file="+red_points_filename)


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
            f.readline().split()
            f.readline()
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
    latitude, longitude, oil_volume, start_date, latitude2, longitude2 = parse_request_params(request)
    url_params = build_request_params_for_file_creation(latitude, longitude, latitude2, longitude2, oil_volume, start_date)
    response = requests.get(
        "http://localhost:8000/service_builder/api/createInputFileForHCMRSpillSimulator/?" + url_params)
    print "<status>" + str(response.status_code) + "</status>"
    filename = ''
    if int(response.status_code) == 200:
        filename = str(response.json()['filename'])
        print filename
    return filename, url_params


def build_request_params_for_file_creation(latitude, longitude, latitude2, longitude2, oil_volume, start_date):
    print(start_date)
    date, daytime = start_date.split(' ')
    print(date)
    year, month, day = date.split('-')
    hours, mins = daytime.split(':')
    url_params = "LATLON=" + str(latitude) + '%20' + str(longitude)
    latlon2 = "&LATLON2="
    if latitude2!='' and longitude2!='':
        latlon2 = "&LATLON2=" + str(latitude2) + '%20' + str(longitude2)

    url_params += latlon2
    url_params += "&DATETIME=" + year + '%20' + month + '%20' + day+'+'+hours+mins
    url_params += "&VOLUME=" + str(oil_volume)
    return url_params


def parse_request_params(request):
    latitude1 = request.GET.get('latitude1')
    latitude2 = request.GET.get('latitude2')
    longitude1 = request.GET.get('longitude1')
    longitude2 = request.GET.get('longitude2')
    start_date = request.GET.get('start_date')
    oil_volume = request.GET.get('oil_volume')
    return latitude1, longitude1, oil_volume, start_date, latitude2, longitude2
