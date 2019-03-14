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
    return render(request, 'hcmr_pilot/load_service.html', {'form': form, 'scenario': scenario, 'execution_steps': execution_steps})


def results(request, exec_instance):
    service_exec = ServiceInstance.objects.get(pk=int(exec_instance))
    visualization_url = service_exec.dataframe_visualizations['v1']
    filename_output = service_exec.arguments['algorithm-arguments'][0]['out_filepath']

    context = {
        'url': visualization_url,
        'out_filepath': filename_output,
    }
    return render(request, 'hcmr_pilot/oilspill-results.html', context)


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
    service = Service.objects.get(pk=service_exec.service_id)
    # 1)Create input file
    service_exec.status = "Creating simulation request"
    service_exec.save()
    filename, url_params = create_inp_file_from_request_and_upload(request)
    # 2)Calculate oil spill
    service_exec.status = "Simulation running"
    service_exec.save()
    found = wait_until_output_ready(url_params, request)
    if found:
        service_exec.status = "Simulation results received"
        service_exec.save()
        filename_output = str(filename).replace("_F.inp", "_F.out")
        hcmr_data_filename = str(filename).replace("_F.inp", ".json")
        red_points_filename = str(filename).replace("_F.inp", ".txt")

        # 3)Transforming data to be shown on map
        service_exec.status = "Transforming data to be shown on map"
        service_exec.save()
        output_path = 'service_builder/static/services_files/hcmr_service_1/' + filename_output
        spill_data, parcel_data = create_json_from_out_file(
            output_path)

        headers_parcel = ["time", "Lat", "Lon", "Dpth", "Status", "Volume(m3)", "Dens", "Visc"]
        parcel_df = DataFrame(parcel_data, columns = headers_parcel)

        print(parcel_df.head(10))
        parcel_df.to_json('visualizer/static/visualizer/files/'+ hcmr_data_filename, orient = 'records')

        # 4)Calculate red points
        red_points_calc.calculate(hcmr_data_filename, red_points_filename)
        service_exec.status = "Calculating oil spill intersections with protected areas"
        service_exec.save()

        # 5)Create Visualization
        visualization_url = "http://" + request.META[
            'HTTP_HOST'] + "/visualizations/map_markers_in_time_hcmr/" + "?markerType=circle&lat_col=Lat&lon_col=Lon" + "&data_file=" + hcmr_data_filename + "&red_points_file=" + red_points_filename

        service_exec.dataframe_visualizations = {"v1": visualization_url}
        service_exec.arguments = {"filter-arguments": [], "algorithm-arguments": [{"out_filepath": filename_output}]}
        service_exec.status = "done"
        service_exec.save()

        # context = {
        #     'url': visualization_url,
        #     'out_filepath': filename_output,
        # }
        # return render(request, 'hcmr_pilot/oilspill-results.html', context)
    else:
        # html = "<html><body>Something went wrong. Please, try again.</body></html>"
        # return HttpResponse(html)
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
    tries = 12
    while (not found) and (tries > 0) and (not error):
        tries -= 1
        time.sleep(2)
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
    spill_infos, wave_model, ocean_model = parse_request_params(request)
    url_params = build_request_params_for_file_creation(spill_infos, wave_model, ocean_model)
    response = requests.get("http://" + request.META['HTTP_HOST'] + "/service_builder/api/createInputFileForHCMRSpillSimulator/?" + url_params)
    print "<status>" + str(response.status_code) + "</status>"
    filename = ''
    if int(response.status_code) == 200:
        filename = str(response.json()['filename'])
        print filename
    return filename, url_params


def build_request_params_for_file_creation(spill_info_list, wave_model, ocean_model):
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
        if (latitude == '' or latitude == 'undefined' or longitude == '' or longitude == 'undefined' or start_date == '' or start_date == 'undefined' or oil_volume == '' or oil_volume == 'undefined' ):
            break
        else:
            spill_infos.append(spill_info)
        print(spill_infos)
    wave_model = request.GET.get('wave_model')
    ocean_model = request.GET.get('hd_model')
    return spill_infos, wave_model, ocean_model


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
