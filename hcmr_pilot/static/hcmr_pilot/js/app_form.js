

var single_marker_layer;
var user_marker = {};
var mode=null;
var first_user_marker = {};
var first_marker_layer;
var second_user_marker = {};
var second_marker_layer;
var third_user_marker ={};
var third_marker_layer;
var fourth_user_marker ={};
var fourth_marker_layer;
var fifth_user_marker ={};
var fifth_marker_layer;

var areaSelect;
var area_bounds;
var bounds = [-90,-180,90,180];
var lock = 0;

var allow_form_submit1 = [true, true];
var allow_form_submit2 = [true, true];
var allow_form_submit3 = [true, true];
var allow_form_submit4 = [true, true];
var allow_form_submit5 = [true, true];
var allow_form_submit_service = [true,true,true]

let MAX_LON_MEDITERRANEAN = 36;
let MIN_LON_MEDITERRANEAN = -7;
let MAX_LAT_MEDITERRANEAN = 45.75;
let MIN_LAT_MEDITERRANEAN = 30.25;

let MAX_LON_AEGEAN_IONIAN = 30;
let MIN_LON_AEGEAN_IONIAN = 19.5;
let MAX_LAT_AEGEAN_IONIAN = 41;
let MIN_LAT_AEGEAN_IONIAN = 30.4;

let AEGEAN_BOUNDS = [35.4893, 22.5923, 41.0727, 27.5273];

function isInsideMediteranean(lat, lon) {
    return !((lat < MIN_LAT_MEDITERRANEAN || lat > MAX_LAT_MEDITERRANEAN) ||
        (lon < MIN_LON_MEDITERRANEAN || lon > MAX_LON_MEDITERRANEAN))
}

function isInsideAegeanIonian(lat, lon) {
    return !((lat < MIN_LAT_AEGEAN_IONIAN || lat > MAX_LAT_AEGEAN_IONIAN) ||
        (lon < MIN_LON_AEGEAN_IONIAN || lon > MAX_LON_AEGEAN_IONIAN))
}

// function check_markers_location() {
//     area_bounds = areaSelect.getBounds();
//     var swlat = Math.round(area_bounds.getSouthWest().lat * 10000) / 10000;
//     var swlon = Math.round(area_bounds.getSouthWest().lng * 10000) / 10000;
//     var nelat = Math.round(area_bounds.getNorthEast().lat * 10000) / 10000;
//     var nelon = Math.round(area_bounds.getNorthEast().lng * 10000) / 10000;
//     bounds = [swlat,swlon,nelat,nelon];
//     var latlng1
//     var latlng1
//     var latlng1
//     var latlng1
// }

function create_new_area_select(area_select_bounds){
    if (areaSelect!== undefined) {
        map.removeLayer(areaSelect);
    }
    $(".leaflet-interactive").remove();
    areaSelect = L.rectangle(area_select_bounds);
    map.addLayer(areaSelect);
    areaSelect.editing.enable();
    area_bounds = areaSelect.getBounds();
    areaSelect.on("edit", function() {
        area_bounds = this.getBounds();
        // bounds = [area_select_bounds[0][0],area_select_bounds[0][1],area_select_bounds[1][0],area_select_bounds[1][1]];
        $('#lat_min').val((area_bounds._southWest.lat).toFixed(4));
        $('#lat_max').val((area_bounds._northEast.lat).toFixed(4));
        $('#lon_min').val((area_bounds._southWest.lng).toFixed(4));
        $('#lon_max').val((area_bounds._northEast.lng).toFixed(4));
    });
    bounds = [area_select_bounds[0][0],area_select_bounds[0][1],area_select_bounds[1][0],area_select_bounds[1][1]];
    $('#lat_min').val(bounds[0]);
    $('#lat_max').val(bounds[2]);
    $('#lon_min').val(bounds[1]);
    $('#lon_max').val(bounds[3]);

}


function tour_guide_senario2(init, tour){
    if (init=== true) {
        var second_scenario_tour = new Tour({
            storage: false,
            template: "<div class='popover tour' style='min-width: 350px; min-height: 120px; color: black;'>" +
            "<div class='arrow'></div>" +
            "<h3 class='popover-title' style='box-shadow: 0px 1px #bfbfbf;'></h3>" +
            "<div class='popover-content'></div>" +
            "<div class='popover-navigation'>" +
            "<button class='btn btn-sm btn-primary' data-role='prev'>« Prev</button>" +
            "<span data-role='separator'>|</span>" +
            "<button class='btn btn-sm btn-primary' data-role='next'>Next »</button>" +
            "<button class='btn btn-sm btn-primary pull-right' data-role='end'>End tour</button>" +
            "</div>" +
            "</div>",
        });
        second_scenario_tour.addStep({
            element: ".spatial-selection",
            placement: "left",
            title: "Area selection",
            content: "Adjust the blue rectangle to the area you wih to investigate. When you finish press the lock area button to lock the coordinates",
        });

        second_scenario_tour.init();
        second_scenario_tour.start(true);
        return second_scenario_tour;
    }else{
        tour.addStep({
                element: ".points-container",
                placement: "left",
                title: "Simulations Points",
                content: "Once you selected the area, select more specifically the points within the selected area. " +
                    "The simulation supports up to five points. Feel free to select whatever number of points. " +
                    "All the simulation points must be placed inside the selected area otherwise the simulation can not be executed. " +
                    "You can go back to edit the location of the selected area",
            });
            tour.addStep({
                element: ".service-parameters",
                placement: "left",
                title: "Service parameters",
                content: "These parameters are common for all the points of the simulation. Time interval is measured in hours, " +
                    "simulation length in hours (max 30 days) and oil density in kg/m3 ",
            });
            tour.next();
            return tour;

    }
}

function tour_guide_senario_1(){
    var first_scenario_tour = new Tour({
            storage: false,
            template: "<div class='popover tour' style='min-width: 350px; min-height: 120px; color: black;'>" +
                "<div class='arrow'></div>" +
                "<h3 class='popover-title' style='box-shadow: 0px 1px #bfbfbf;'></h3>" +
                "<div class='popover-content'></div>" +
                "<div class='popover-navigation'>" +
                "<button class='btn btn-sm btn-primary' data-role='prev'>« Prev</button>" +
                "<span data-role='separator'>|</span>" +
                "<button class='btn btn-sm btn-primary' data-role='next'>Next »</button>" +
                "<button class='btn btn-sm btn-primary pull-right' data-role='end'>End tour</button>" +
                "</div>" +
                "</div>",
    });

    first_scenario_tour.addStep({
        element: ".application-header",
        placement: "left",
        title: "Oil spill dispersion forecast",
        // duration: 3500,
        content: "Perform an oil spill dispersion simulation. Select a starting point on the map and provide all the necessary information.",
    });
    first_scenario_tour.addStep({
        element: ".lat-container",
        placement: "left",
        title: "Click on the map",
        // duration: 3500,
        content: "Click on the map to select the point of an oil spill incident or add manually position latitude and longitude.",
    });
    first_scenario_tour.addStep({
        element: ".vis-startdate-container",
        placement: "left",
        title: "Datetime Selection",
        content: "Set the oil spill starting date and time. For historical simulations, you can choose date and time up to one year back.",
    });
    first_scenario_tour.addStep({
        element: ".oil-volume-container",
        placement: "left",
        title: "Oil volume input",
        content: "Set the volume of the oil spilled in the sea.",
    });

    first_scenario_tour.addStep({
        element: ".vis-duration-container",
        placement: "left",
        title: "Simulation duration",
        content: "Set the duration of the oil volume release in the sea.",
    });

    first_scenario_tour.addStep({
        element: ".simulation-length-container",
        placement: "left",
        title: "Simulation length",
        content: "Set the duration of the requested simulation in hours (30 days maximum length).",
    });
    first_scenario_tour.addStep({
        element: ".time-interval-container",
        placement: "left",
        title: "Time interval",
        content: "Set the time step of the output results.",
    });

    first_scenario_tour.addStep({
        element: "#sel2",
        placement: "left",
        title: "Ocean Circulation Model",
        duration: 3500,
        content: "Choose ocean circulation model. The forecasting product will be used as the hydrodynamic input for the oil spill simulation.",
    });
    first_scenario_tour.addStep({
        element: "#sel1",
        placement: "left",
        title: "Wave Model",
        duration: 3500,
        content: "Choose the wave model. The forecasting product will be used as wave input for the oil spill simulation.",
    });
    first_scenario_tour.addStep({
        element: ".checkbox",
        placement: "left",
        title: "Additional layers",
        duration: 3500,
        content: "(Optional) Select additional layers to be added to the output of the simulation.",
    });

    first_scenario_tour.addStep({
        element: ".service-buttons",
        placement: "left",
        title: "Execution",
        duration: 3500,
        content: "All set. Ready to run the service!",
    });

    first_scenario_tour.init();
    first_scenario_tour.start(true);
}

function check_marker_position(lat, lon, user_marker, bounds, lat_selector, lon_selector,point, offset){
    if (isInsideAegeanIonian(lat,lon)) {
        $("#sel1"+point).dropdown("set selected", "202");
        $("#sel2"+point).dropdown("set selected", "001");
        lat_selector.val(lat.toFixed(4));
        lon_selector.val(lon.toFixed(4));
    } else if (isInsideMediteranean(lat,lon)) {
        $("#sel1"+point).dropdown("set selected", "201");
        $("#sel2"+point).dropdown("set selected", "002");
        lat_selector.val(lat.toFixed(4));
        lon_selector.val(lon.toFixed(4));
    } else {
        alert("Point outside of Mediterranean sea. Please select another point");
        var latlng = L.latLng((((bounds[0] + bounds[2]) / 2)+ offset[0]).toFixed(4), (((bounds[1] + bounds[3]) / 2)+ offset[1]).toFixed(4));
        user_marker.setLatLng(latlng).update(user_marker);
        lat_selector.val((((bounds[0] + bounds[2]) / 2)+ offset[0]).toFixed(4));
        lon_selector.val((((bounds[1] + bounds[3]) / 2)+ offset[1]).toFixed(4));
        // lat_selector.trigger('change');
        // lon_selector.trigger('change');
        $("#sel1"+point).dropdown("set selected", "202");
        $("#sel2"+point).dropdown("set selected", "001");
    }
};

function check_marker_inside_area_select(lat, lon, user_marker,bounds, lat_selector, lon_selector, point, offset){
    if ((lat< bounds[0]) || (lon<bounds[1]) || (lat>bounds[2])|| (lon>bounds[3])){
        alert("Point outside of the selected area. Please select another point");
        var latlng = L.latLng((((bounds[0] + bounds[2]) / 2)+offset[0]).toFixed(4), (((bounds[1] + bounds[3]) / 2)+offset[1]).toFixed(4));
        user_marker.setLatLng(latlng).update(user_marker);
        lat_selector.val((((bounds[0] + bounds[2]) / 2)+ offset[0]).toFixed(4));
        lon_selector.val((((bounds[1] + bounds[3]) / 2)+ offset[1]).toFixed(4));
        // lat_selector.trigger('change');
        // lon_selector.trigger('change');
        lat = parseFloat(lat_selector.val());
        lon = parseFloat(lon_selector.val());
    }else{
        var latlng = L.latLng(lat, lon);
        user_marker.setLatLng(latlng).update(user_marker);
    }
    check_marker_position(lat, lon, user_marker, bounds, lat_selector,lon_selector, point, offset);
}

function check_sim_len_options(){
    $('#simulation_length_hist').parent().find('div').removeClass('disabled');
    var starting_date = new Date($("#startdatepicker input").val());
    var now = new Date();
    now.setDate(now.getDate()+4);
    var oneDay = 24*60*60*1000;
    var diffDays = Math.round(Math.abs((starting_date.getTime() - now.getTime())/(oneDay)));
    var diff_dec_days = (Math.abs((starting_date.getTime() - now.getTime())/(oneDay)).toFixed(2));
    if (diff_dec_days < 30){
        var diff = (30-diff_dec_days)*24;
        $('#simulation_length_hist').parent().find('div div').each(function (el) {
            var ist = $(this).attr('data-value');
            if (ist > diff_dec_days*24) {
                $(this).addClass('disabled');
            }
        });

    }

}

function interactive_form(onLocationfound, user_marker){
    var allow_form_submit = [true, true, true, true, true, true];
    check_sim_len_options();
    $('#lat').on('input',function () {
        allow_form_submit = missing_parameter($('#lat'), allow_form_submit, 'latitude', 0, '#run-service-btn','latitude' );
        if($('#lat').val()<-90){
            $('#lat').val((-90).toFixed(4));
        }else if($('#lat').val()>90){
            $('#lat').val((90).toFixed(4));
        }
        onLocationfound({latlng:[$('#lat').val(),$('#lon').val()]});
    });
    $('#lat').on('change',function () {
        if (($('#lat').val() !== '') && ($('#lat').val() !== undefined) && ($('#lat').val()!== null)) {
            check_marker_position(parseFloat($('#lat').val()),parseFloat($('#lon').val()),user_marker, AEGEAN_BOUNDS,$('#lat'),$('#lon'),'',[0,0])
        }
    });
    $('#lon').on('input',function () {
        allow_form_submit = missing_parameter($('#lon'), allow_form_submit, 'longitude', 1, '#run-service-btn','longitude');
        if($('#lon').val()<-180){
            $('#lon').val((-180).toFixed(4));
        }else if($('#lon').val()>180){
            $('#lon').val((180).toFixed(4));
        }
        onLocationfound({latlng:[$('#lat').val(),$('#lon').val()]});
    });
    $('#lon').on('change',function () {
        if (($('#lon').val() !== '') && ($('#lon').val() !== undefined) && ($('#lon').val()!== null)) {
            check_marker_position(parseFloat($('#lat').val()),parseFloat($('#lon').val()),user_marker, AEGEAN_BOUNDS,$('#lat'),$('#lon'),'',[0,0])
        }
    });
    $('#startdatepicker input').on('change',function () {
        allow_form_submit = missing_parameter($('#startdatepicker input'), allow_form_submit, 'date', 2, '#run-service-btn','date');
        check_sim_len_options();
    });
    $('#startdatepicker input').on('input',function () {
        allow_form_submit = missing_parameter($('#startdatepicker input'), allow_form_submit, 'date', 2, '#run-service-btn','date');
        check_sim_len_options();
    });
    $('#oil_volume').on('input',function(){
        allow_form_submit = missing_parameter($('#oil_volume'), allow_form_submit, 'oil-volume', 3, '#run-service-btn','oil-volume');
        if ($('#oil_volume').val()<0){
            $('#oil_volume').val(0);
        }
    });
    $('#oil_density').on('input',function(){
        allow_form_submit = missing_parameter($('#oil_density'), allow_form_submit, 'oil-density', 4, '#run-service-btn','oil-density');
        if ($('#oil_density').val()<0){
            $('#oil_density').val(0);
        }
    });
    $('#vis_duration').on('input',function(){
        allow_form_submit = missing_parameter($('#vis_duration'), allow_form_submit, 'duration', 5, '#run-service-btn','duration');
        if ($('#vis_duration').val()<0){
            $('#vis_duration').val(0);
        }
    });
    $('#sel2').on('change',function () {
        if ($('#sel2').val()==='003'){
            $('#sel1').parent().dropdown('set selected','203');
        }
    });
    $('#sel1').on('change',function () {
        if ($('#sel1').val()==='203'){
            $('#sel2').parent().dropdown('set selected','003');
        }
    });
}

function interactive_multi_point_service_form(){
    $('#vis_duration').on('input',function(){
        allow_form_submit_service = missing_parameter($('#vis_duration'), allow_form_submit_service, 'duration', 0, '#run-service-btn','duration');
        if ($('#vis_duration').val()<0){
            $('#vis_duration').val(0);
        }
    });

    $('#oil_density').on('input',function(){
        allow_form_submit_service = missing_parameter($('#oil_density'), allow_form_submit_service, 'oil-density', 1, '#run-service-btn','oil-density');
        if ($('#oil_density').val()<0){
            $('#oil_density').val(0);
        }
    });
    $('#startdatepicker input').on('change',function () {
        allow_form_submit_service = missing_parameter($('#startdatepicker input'), allow_form_submit_service, 'date', 2, '#run-service-btn','date');
        check_sim_len_options();
    });
    $('#startdatepicker input').on('input',function () {
        allow_form_submit_service = missing_parameter($('#startdatepicker input'), allow_form_submit_service, 'date', 2, '#run-service-btn','date');
        check_sim_len_options();
    });

}

function interactive_multi_point_form(onLocationfound, user_marker, lat, lon, point, allow_form_submit, offset){
    check_sim_len_options();
    lat.on('input',function () {
        allow_form_submit = missing_parameter(lat, allow_form_submit, 'latitude'+point, 0, '#run-service-btn','latitude of Point '+point);
        if(lat.val()<-90){
            lat.val((-90).toFixed(4));
        }else if(lat.val()>90){
            lat.val((90).toFixed(4));
        }
        onLocationfound({latlng:[lat.val(),lon.val()]});
    });
    lat.on('change',function () {
        if ((lat.val() !== '') && (lat.val() !== undefined) && (lat.val()!== null)) {
            check_marker_inside_area_select(parseFloat(lat.val()), parseFloat(lon.val()),user_marker,bounds,lat,lon,'-point'+point,offset);
        }
    });
    lon.on('input',function () {
        allow_form_submit = missing_parameter(lon, allow_form_submit, 'longitude'+point, 1, '#run-service-btn', 'longitude of Point '+point);
        if(lon.val()<-180){
            lon.val((-180).toFixed(4));
        }else if(lon.val()>180){
            lon.val((180).toFixed(4));
        }
        onLocationfound({latlng:[lat.val(),lon.val()]});
    });
    lon.on('change',function () {
        if ((lon.val() !== '') && (lon.val() !== undefined) && (lon.val()!== null)) {
             check_marker_inside_area_select(parseFloat(lat.val()), parseFloat(lon.val()),user_marker,bounds,lat,lon,'-point'+point, offset);
        }
    });

}

function check_bounds_min_max(input1, input2, allow_submit, parameter, parameter_id){
        if (parseFloat(input1.val())>=parseFloat(input2.val())){
                if(allow_submit[parameter_id]===true) {
                    $("<div class='conf-error-message limit_oob_message'>*Minimum "+parameter+" must be smaller than maximum.</div>").insertBefore("#run-service-btn");
                    $('#lock_area').addClass('disabled');
                }
                allow_submit[parameter_id] = false;
        }else{
            allow_submit[parameter_id] = true;
            $('.limit_oob_message').remove();
            if(check_list(allow_submit)) {
                $('#lock_area').removeClass('disabled');
            }
        }
        return allow_submit
    }

function missing_parameter(col_select, allow_submit, parameter_name, parameter_id, disable_button, parameter_name_text) {
    if ((col_select.val() === null) || (col_select.val().length === 0)) {
        if (allow_submit[parameter_id] === true) {
            $(disable_button).addClass('disabled');
            $("<div class='conf-error-message " + parameter_name + "_missing_error'>* Selection of " + parameter_name_text + " is required.</div>").insertBefore(disable_button);
        }
        allow_submit[parameter_id] = false;
    }
    else {
        allow_submit[parameter_id] = true;
        $('.' + parameter_name + '_missing_error').remove();
        if (check_list(allow_submit)&&check_list(allow_form_submit1)&&check_list(allow_form_submit2)&&check_list(allow_form_submit3)&&check_list(allow_form_submit4)&&check_list(allow_form_submit5)&&check_list(allow_form_submit_service)) {
            $(disable_button).removeClass('disabled');
        }
    }
    return allow_submit
}

function check_list(list){
    var flag = true;
    for(var i=0; i<list.length; i++){
        if(list[i]===false){
            flag=false;
        }
    }
    return flag;
}

function create_new_oilspill(user_marker, lat_selector, lon_selector, offset, name_oil_spill, map, icon,point){
    user_marker = L.marker([((bounds[0] + bounds[2]) / 2)+offset[0], ((bounds[1] + bounds[3]) / 2)+offset[1]], {draggable: true}).bindPopup(name_oil_spill).addTo(map);
    var marker_layer = L.layerGroup(user_marker);
    user_marker.on('dragend', function (e) {
        check_marker_inside_area_select(e.target._latlng.lat, e.target._latlng.lng,user_marker, bounds,lat_selector, lon_selector,point,offset);
    });
    user_marker.setIcon(icon);
    map.addLayer(marker_layer);
    map.locate();
    lat_selector.val((bounds[0] + bounds[2]) / 2);
    lon_selector.val((bounds[1] + bounds[3]) / 2);
    // map.setView([(bounds[0] + bounds[2]) / 2,(bounds[1] + bounds[3]) / 2], 8);
    check_marker_position(((bounds[0] + bounds[2]) / 2),((bounds[1] + bounds[3]) / 2),user_marker,bounds, lat_selector, lon_selector,point, offset);
    return user_marker
}

function interactive_area_select() {
    var allow_form_submit = [true, true, true, true, true, true];
    $('#lat_min').on('input',function () {
        allow_form_submit = missing_parameter($('#lat_min'), allow_form_submit, 'minimum-latitude', 0, '#lock_area', 'minimum latitude');
        allow_form_submit = check_bounds_min_max($('#lat_min'), $('#lat_max'), allow_form_submit, 'latitude', 4);
        if($('#lat_min').val()<-90){
            $('#lat_min').val((-90).toFixed(4));
        }else if($('#lat_min').val()>90){
            $('#lat_min').val((90).toFixed(4));
        }
    });
    $('#lat_min').on('change',function () {
        if (($('#lat_min').val() !== '') && ($('#lat_min').val() !== undefined) && ($('#lat_min').val()!== null)) {
            // check_area_position([[$('#lat_min').val(),$('#lon_min').val()],[$('#lat_max').val(),$('#lon_max').val()]]);
            create_new_area_select([[$('#lat_min').val(),$('#lon_min').val()],[$('#lat_max').val(),$('#lon_max').val()]])
        }
    });
    $('#lat_max').on('input',function () {
        allow_form_submit = missing_parameter($('#lat_max'), allow_form_submit, 'maximum-latitude', 1, '#lock_area', 'maximum latitude');
        allow_form_submit = check_bounds_min_max($('#lat_min'), $('#lat_max'), allow_form_submit, 'latitude', 4);
        if($('#lat_max').val()<-90){
            $('#lat_max').val((-90).toFixed(4));
        }else if($('#lat_max').val()>90){
            $('#lat_max').val((90).toFixed(4));
        }
    });
    $('#lat_max').on('change',function () {
        if (($('#lat_min').val() !== '') && ($('#lat_min').val() !== undefined) && ($('#lat_min').val()!== null)) {
            // check_area_position([[$('#lat_min').val(),$('#lon_min').val()],[$('#lat_max').val(),$('#lon_max').val()]]);
            create_new_area_select([[$('#lat_min').val(),$('#lon_min').val()],[$('#lat_max').val(),$('#lon_max').val()]])
        }
    });
    $('#lon_min').on('input',function () {
        allow_form_submit = missing_parameter($('#lon_min'), allow_form_submit, 'minimum-longitude', 2, '#lock_area', 'minimum longitude');
        allow_form_submit = check_bounds_min_max($('#lon_min'), $('#lon_max'), allow_form_submit, 'longitude', 5);
        if($('#lon_min').val()<-180){
            $('#lon_min').val((-180).toFixed(4));
        }else if($('#lon_min').val()>180){
            $('#lon_min').val((180).toFixed(4));
        }
    });
    $('#lon_min').on('change',function () {
        if (($('#lat_min').val() !== '') && ($('#lat_min').val() !== undefined) && ($('#lat_min').val()!== null)) {
            // check_area_position([[$('#lat_min').val(),$('#lon_min').val()],[$('#lat_max').val(),$('#lon_max').val()]]);
            create_new_area_select([[$('#lat_min').val(),$('#lon_min').val()],[$('#lat_max').val(),$('#lon_max').val()]])
        }
    });
    $('#lon_max').on('input',function () {
        allow_form_submit = missing_parameter($('#lon_max'), allow_form_submit, 'maximum-longitude', 3, '#lock_area', 'maximum longitude');
        allow_form_submit = check_bounds_min_max($('#lon_min'), $('#lon_max'), allow_form_submit, 'longitude', 5);
        if($('#lon_max').val()<-180){
            $('#lon_max').val((-180).toFixed(4));
        }else if($('#lon_max').val()>180){
            $('#lon_max').val((180).toFixed(4));
        }
    });
    $('#lon_max').on('change',function () {
        if (($('#lat_min').val() !== '') && ($('#lat_min').val() !== undefined) && ($('#lat_min').val()!== null)) {
            // check_area_position([[$('#lat_min').val(),$('#lon_min').val()],[$('#lat_max').val(),$('#lon_max').val()]]);
            create_new_area_select([[$('#lat_min').val(),$('#lon_min').val()],[$('#lat_max').val(),$('#lon_max').val()]])
        }
    });


}
//
function check_area_position(area) {
    if (!isInsideMediteranean(area[0][0], area[0][1])||!isInsideMediteranean(area[0][0], area[1][1])||!isInsideMediteranean(area[1][0], area[1][1])||!isInsideMediteranean(area[1][0], area[0][1])) {
        create_new_area_select([[MIN_LAT_MEDITERRANEAN + 1, MIN_LON_MEDITERRANEAN + 1], [MAX_LAT_MEDITERRANEAN - 1, MAX_LON_MEDITERRANEAN - 1]]);
        alert("Area outside of Mediterranean sea. Please re-define the area.");
    }
}

$(document).ready(function() {
    map_init();
    var scenario = $('.scenario').data('id');
    $('.ui.dropdown').dropdown();
    $('#time_interval').parent().css('min-width','13rem');
    $('#time_interval').parent().addClass("form-control");
    $('#time_interval').parent().css('top','3px');
    $('#time_interval').dropdown('set selected', 2);
    $('#simulation_length_hist').dropdown('set selected', 24);
    $('#simulation_length_hist').parent().css('min-width','13rem');
    $('#simulation_length_hist').parent().addClass("form-control");
    $('#simulation_length_hist').parent().css('top','3px');
    $('#sel2').parent().css('min-width','100%');
    $('#sel1').parent().css('min-width','100%');
    $('.glyphicon-calendar').css('top','-15px');
    var startDate = new Date();
    var endDate = new Date();
    startDate.setFullYear(startDate.getFullYear() - 1);
    startDate.setHours(0,0,0,0);
    if(scenario === 2){
         var startpick = $('#startdatepicker').datetimepicker({
            autoclose: true,
            pickerPosition: 'bottom-left',
            startDate: startDate,
            endDate: endDate,
            initialDate: endDate
        });
        startpick.datetimepicker('update',endDate);
        $('#run-service-btn').hide();
        var second_scenario_tour = tour_guide_senario2(true,'');
        create_new_area_select([[MIN_LAT_MEDITERRANEAN+2,MIN_LON_MEDITERRANEAN+2],[MAX_LAT_MEDITERRANEAN-2,MAX_LON_MEDITERRANEAN-2]]);
        interactive_area_select();
        interactive_multi_point_service_form();
        // var datetimepicker_list = datetimepicker_initialisation(startDate, endDate);
        // var marker_list = markers_initialisation();
        $('#lock_area').on('click', function(e){
            $('#run-service-btn').show();
            lock = 1;
            areaSelect.editing.disable();
            $('.spatial-selection').hide();
            $('.points-container').show();
            $('.service-buttons').show();
            $('#unlock-area').show();
            bounds=[];
            bounds[0] = parseFloat($('#lat_min').val());
            bounds[2] = parseFloat($('#lat_max').val());
            bounds[1] = parseFloat($('#lon_min').val());
            bounds[3] = parseFloat($('#lon_max').val());

            var blueIcon = new L.Icon({
                iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png'
            });
            first_user_marker = create_new_oilspill(first_user_marker,$('#lat'), $('#lon'), [0,0],'Oil-Spill-1',map,blueIcon,'-point1');
            onLocationfound1 = function(e){
                first_user_marker.setLatLng(e.latlng).update();
            };
            map.on('locationfound', onLocationfound1);
            interactive_multi_point_form(onLocationfound1,first_user_marker,$('#lat'), $('#lon'),'1',allow_form_submit1,[0,0]);
            tour_guide_senario2(false, second_scenario_tour);
            map.setView([(bounds[0] + bounds[2]) / 2,(bounds[1] + bounds[3]) / 2], 6);
        });

        $('#unlock-area').on('click', function(e){
            $('#run-service-btn').hide();
            areaSelect.editing.enable();
            lock = 0;
            if (first_user_marker != undefined) {
                map.removeLayer(first_user_marker);
            }
            if (second_user_marker != undefined) {
                map.removeLayer(second_user_marker);
            }
            if (third_user_marker != undefined) {
                map.removeLayer(third_user_marker);
            }
            if (fourth_user_marker != undefined) {
                map.removeLayer(fourth_user_marker);
            }
            if (fifth_user_marker != undefined) {
                map.removeLayer(fifth_user_marker);
            }
            $("#point2_form").removeClass("in");
            $("#point2_form").removeClass("active");
            $("#point3_form").removeClass("in");
            $("#point3_form").removeClass("active");
            $("#point4_form").removeClass("in");
            $("#point4_form").removeClass("active");
            $("#point5_form").removeClass("in");
            $("#point5_form").removeClass("active");
            $('.nav-item').children('a[href="#point2_form"]').removeAttr('data-toggle');
            $('.nav-item').children('a[href="#point2_form"]').parent().removeClass('active');
            $('.nav-item').children('a[href="#point2_form"]').parent().addClass('disabled');
            $('.nav-item').children('a[href="#point3_form"]').removeAttr('data-toggle');
            $('.nav-item').children('a[href="#point3_form"]').parent().removeClass('active');
            $('.nav-item').children('a[href="#point3_form"]').parent().addClass('disabled');
            $('.nav-item').children('a[href="#point4_form"]').removeAttr('data-toggle');
            $('.nav-item').children('a[href="#point4_form"]').parent().removeClass('active');
            $('.nav-item').children('a[href="#point4_form"]').parent().addClass('disabled');
            $('.nav-item').children('a[href="#point5_form"]').removeAttr('data-toggle');
            $('.nav-item').children('a[href="#point5_form"]').parent().removeClass('active');
            $('.nav-item').children('a[href="#point5_form"]').parent().addClass('disabled');

            $("#point1_form").addClass("in");
            $("#point1_form").addClass("active");
            $('.nav-item').children('a[href="#point1_form"]').parent().addClass('active');
            $('.spatial-selection').show();
            $('.points-container').hide();
            $('.service-buttons').hide();
            $('#unlock-area').hide();
            area_bounds = areaSelect.getBounds();
            var swlat = Math.round(area_bounds.getSouthWest().lat * 10000) / 10000;
            var swlon = Math.round(area_bounds.getSouthWest().lng * 10000) / 10000;
            var nelat = Math.round(area_bounds.getNorthEast().lat * 10000) / 10000;
            var nelon = Math.round(area_bounds.getNorthEast().lng * 10000) / 10000;
            bounds = [swlat,swlon,nelat,nelon];
            map.setView([(bounds[0] + bounds[2]) / 2,(bounds[1] + bounds[3]) / 2], 6);
        });

        $(".new_point").click(function(){
            $('.nav li.active').next('li').removeClass('disabled');
            var tabid = $('.nav li.active').children('a[data-toggle="pill"]').attr('href');
            $(tabid).removeClass('active');
            $(tabid).removeClass('in');
            $('.nav li.active').next('li').find('a').attr("data-toggle","pill");
            $('.nav li.active').next('li').addClass('active');
            $('.nav li.active').prev('li').removeClass('active');
            var tabid2 = $('.nav li.active').children('a[data-toggle="pill"]').attr('href');
            $(tabid2).addClass('active');
            $(tabid2).addClass('in');

            if ( tabid2 === "#point2_form"){
                if (second_user_marker != undefined) {
                    map.removeLayer(second_user_marker);
                }
                var redIcon = new L.Icon({
                    iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'
                });
                second_user_marker = create_new_oilspill(second_user_marker,$('#lat2'), $('#lon2'), [(bounds[2]-bounds[0])/4, (bounds[3]-bounds[1])/4 ],'Oil-Spill-2',map,redIcon,'-point2');
                onLocationfound2 = function(e){
                    second_user_marker.setLatLng(e.latlng).update();
                };
                map.on('locationfound', onLocationfound2);
                interactive_multi_point_form(onLocationfound2,second_user_marker,$('#lat2'), $('#lon2'),'2',allow_form_submit2,[(bounds[2]-bounds[0])/4, (bounds[3]-bounds[1])/4 ]);
            }
            else if(tabid2 === "#point3_form"){
                if (third_user_marker != undefined) {
                    map.removeLayer(third_user_marker);
                }
                var greenIcon = new L.Icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png'
                });
                third_user_marker = create_new_oilspill(third_user_marker,$('#lat3'), $('#lon3'), [-(bounds[2]-bounds[0])/4, (bounds[3]-bounds[1])/4 ],'Oil-Spill-3',map,greenIcon,'-point3');
                onLocationfound3 = function(e){
                    third_user_marker.setLatLng(e.latlng).update();
                };
                map.on('locationfound', onLocationfound3);
                interactive_multi_point_form(onLocationfound3,third_user_marker,$('#lat3'), $('#lon3'),'3',allow_form_submit3, [-(bounds[2]-bounds[0])/4, (bounds[3]-bounds[1])/4 ]);

                // // var startpick = $('#startdatepicker3').datetimepicker({
                // //     autoclose: true,
                // //     pickerPosition: 'top-left',
                // //
                // // });
                // if (third_user_marker != undefined) {
                //     map.removeLayer(third_user_marker);
                // }
                // var greenIcon = new L.Icon({
                //     iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png'
                // });
                // third_user_marker = L.marker([((bounds[0] + bounds[2]) / 2) - x_mov, ((bounds[1] + bounds[3] ) / 2) + y_mov ], {draggable:true}, {icon: greenIcon}).bindPopup("Third Marker").addTo(map);
                // third_user_marker.setIcon(greenIcon);
                // third_marker_layer = L.layerGroup(third_user_marker);
                // map.addLayer(third_marker_layer);
                //
                // third_user_marker.on('dragend', function (e) {
                //     $('#lat3').val(e.target._latlng.lat);
                //     $('#lon3').val(e.target._latlng.lng);
                // });
                // var lat = ((bounds[0] + bounds[2] ) / 2) - 0.1;
                // var lng = ((bounds[1] + bounds[3] ) / 2) + 0.1;
                // $('#lat3').val(lat);
                // $('#lon3').val(lng);

            }
            else if (tabid2 === "#point4_form"){
                if (fourth_user_marker != undefined) {
                    map.removeLayer(fourth_user_marker);
                }
                var orangeIcon = new L.Icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png'
                });
                fourth_user_marker = create_new_oilspill(fourth_user_marker,$('#lat4'), $('#lon4'), [-(bounds[2]-bounds[0])/4, -(bounds[3]-bounds[1])/4 ],'Oil-Spill-4',map,orangeIcon,'-point4');
                onLocationfound4 = function(e){
                    fourth_user_marker.setLatLng(e.latlng).update();
                };
                map.on('locationfound', onLocationfound4);
                interactive_multi_point_form(onLocationfound4,fourth_user_marker,$('#lat4'), $('#lon4'),'4',allow_form_submit4,[-(bounds[2]-bounds[0])/4, -(bounds[3]-bounds[1])/4 ]);


                // // var startpick = $('#startdatepicker4').datetimepicker({
                // //     autoclose: true,
                // //     pickerPosition: 'top-left',
                // //
                // // });
                // if (fourth_user_marker != undefined) {
                //     map.removeLayer(fourth_user_marker);
                // }
                // var orangeIcon = new L.Icon({
                //     iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png'
                // });
                // fourth_user_marker = L.marker([((bounds[0] + bounds[2] ) / 2) + x_mov, ((bounds[1] + bounds[3]) / 2) - y_mov], {draggable:true}, {icon: greenIcon}).bindPopup("Fourth Marker").addTo(map);
                // fourth_user_marker.setIcon(orangeIcon);
                // fourth_marker_layer = L.layerGroup(fourth_user_marker);
                // map.addLayer(fourth_marker_layer);
                //
                // fourth_user_marker.on('dragend', function (e) {
                //     $('#lat4').val(e.target._latlng.lat);
                //     $('#lon4').val(e.target._latlng.lng);
                // });
                // var lat = ((bounds[0] + bounds[2] ) / 2) + 0.1;
                // var lng = ((bounds[1] + bounds[3] ) / 2) - 0.1;
                // $('#lat4').val(lat);
                // $('#lon4').val(lng);
            }
            else if (tabid2 === "#point5_form"){

                if (fifth_user_marker != undefined) {
                    map.removeLayer(fifth_user_marker);
                }
                var blackIcon = new L.Icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-black.png'
                });
                fifth_user_marker = create_new_oilspill(fifth_user_marker,$('#lat5'), $('#lon5'), [(bounds[2]-bounds[0])/4, -(bounds[3]-bounds[1])/4 ],'Oil-Spill-5',map,blackIcon,'-point5');
                onLocationfound5 = function(e){
                    fifth_user_marker.setLatLng(e.latlng).update();
                };
                map.on('locationfound', onLocationfound5);
                interactive_multi_point_form(onLocationfound5,fifth_user_marker,$('#lat5'), $('#lon5'),'5',allow_form_submit5, [(bounds[2]-bounds[0])/4, -(bounds[3]-bounds[1])/4 ]);

                // // var startpick = $('#startdatepicker5').datetimepicker({
                // //     autoclose: true,
                // //     pickerPosition: 'top-left',
                // //
                // // });
                // if (fifth_user_marker != undefined) {
                //     map.removeLayer(fifth_user_marker);
                // }
                // var blackIcon = new L.Icon({
                //     iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-black.png'
                // });
                // fifth_user_marker = L.marker([((bounds[0] + bounds[2] ) / 2) + x_mov, ((bounds[1] + bounds[3] ) / 2) + y_mov], {draggable:true}, {icon: greenIcon}).bindPopup("Fourth Marker").addTo(map);
                // fifth_user_marker.setIcon(blackIcon);
                // fifth_marker_layer = L.layerGroup(fifth_user_marker);
                // map.addLayer(fifth_marker_layer);
                //
                // fifth_user_marker.on('dragend', function (e) {
                //     $('#lat5').val(e.target._latlng.lat);
                //     $('#lon5').val(e.target._latlng.lng);
                // });
                // var lat = ((bounds[0] + bounds[2] ) / 2) + 0.1;
                // var lng = ((bounds[1] + bounds[3] ) / 2) + 0.1;
                // $('#lat5').val(lat);
                // $('#lon5').val(lng);
            }

        });

        $('#remove_point2').click(function () {
            allow_form_submit2 = [true, true, true, true, true];
            $('#lat2').val("");
            $('#lon2').val("");
            $('#oil_volume2').val(10000);
            $('#vis_duration2').val(0);
            datetimepicker_list[1].datetimepicker('update',endDate);
            $('#lat2').off();
            $('#lon2').off();
            $('#oil_volume2').off();
            $('#vis_duration2').off();
            $('#startdatepicker2 input').off();

            if (second_user_marker != undefined) {
                map.removeLayer(second_user_marker);
            }
            $("#point2_form").removeClass("in");
            $("#point2_form").removeClass("active");
            $("#point1_form").addClass("in");
            $("#point1_form").addClass("active");
            $('.nav-item').children('a[href="#point2_form"]').removeAttr('data-toggle');
            $('.nav-item').children('a[href="#point2_form"]').parent().removeClass('active');
            $('.nav-item').children('a[href="#point2_form"]').parent().addClass('disabled');
            $('.nav-item').children('a[href="#point1_form"]').parent().addClass('active');
        });

        $('#remove_point3').click(function () {
            allow_form_submit3 = [true, true, true, true, true];
            $('#lat3').val("");
            $('#lon3').val("");
            $('#oil_volume3').val(10000);
            $('#vis_duration3').val(0);
            datetimepicker_list[2].datetimepicker('update',endDate);
            $('#lat3').off();
            $('#lon3').off();
            $('#oil_volume3').off();
            $('#vis_duration3').off();
            $('#startdatepicker3 input').off();
            if (third_user_marker != undefined) {
                map.removeLayer(third_user_marker);
            }
            $("#point3_form").removeClass("in");
            $("#point3_form").removeClass("active");
            $("#point1_form").addClass("in");
            $("#point1_form").addClass("active");
            $('.nav-item').children('a[href="#point3_form"]').removeAttr('data-toggle');
            $('.nav-item').children('a[href="#point3_form"]').parent().removeClass('active');
            $('.nav-item').children('a[href="#point3_form"]').parent().addClass('disabled');
            $('.nav-item').children('a[href="#point1_form"]').parent().addClass('active');
        });

        $('#remove_point4').click(function () {
            allow_form_submit4 = [true, true, true, true, true];
            $('#lat4').val("");
            $('#lon4').val("");
            $('#oil_volume4').val(10000);
            $('#vis_duration4').val(0);
            datetimepicker_list[3].datetimepicker('update',endDate);
            $('#lat4').off();
            $('#lon4').off();
            $('#oil_volume4').off();
            $('#vis_duration4').off();
            $('#startdatepicker4 input').off();
            if (fourth_user_marker != undefined) {
                map.removeLayer(fourth_user_marker);
            }
            $("#point4_form").removeClass("in");
            $("#point4_form").removeClass("active");
            $("#point1_form").addClass("in");
            $("#point1_form").addClass("active");
            $('.nav-item').children('a[href="#point4_form"]').removeAttr('data-toggle');
            $('.nav-item').children('a[href="#point4_form"]').parent().removeClass('active');
            $('.nav-item').children('a[href="#point4_form"]').parent().addClass('disabled');
            $('.nav-item').children('a[href="#point1_form"]').parent().addClass('active');
        });

        $('#remove_point5').click(function () {
            allow_form_submit5 = [true, true, true, true, true];
            $('#lat5').val("");
            $('#lon5').val("");
            $('#oil_volume5').val(10000);
            $('#vis_duration5').val(0);
            datetimepicker_list[4].datetimepicker('update',endDate);
            $('#lat5').off();
            $('#lon5').off();
            $('#oil_volume5').off();
            $('#vis_duration5').off();
            $('#startdatepicker5 input').off();
            if (fifth_user_marker != undefined) {
                map.removeLayer(fifth_user_marker);
            }
            $("#point5_form").removeClass("in");
            $("#point5_form").removeClass("active");
            $("#point1_form").addClass("in");
            $("#point1_form").addClass("active");
            $('.nav-item').children('a[href="#point5_form"]').removeAttr('data-toggle');
            $('.nav-item').children('a[href="#point5_form"]').parent().removeClass('active');
            $('.nav-item').children('a[href="#point5_form"]').parent().addClass('disabled');
            $('.nav-item').children('a[href="#point1_form"]').parent().addClass('active');
        });
    }



    if (scenario === 1) {
        var startpick = $('#startdatepicker').datetimepicker({
            autoclose: true,
            pickerPosition: 'bottom-left',
            startDate: startDate,
            endDate: endDate,
            initialDate: endDate
        });
        startpick.datetimepicker('update',endDate);
        $('#lat').val((38.2810).toFixed(4));
        $('#lon').val((25.0598).toFixed(4));
        first_user_marker = L.marker([38.2810, 25.0598], {draggable: true}).bindPopup("First Marker").addTo(map);
        first_marker_layer = L.layerGroup(first_user_marker);
        onLocationfound = function(e){
            first_user_marker.setLatLng(e.latlng).update();
        };
        first_user_marker.on('dragend', function (e) {
            check_marker_position(e.target._latlng.lat, e.target._latlng.lng,first_user_marker, AEGEAN_BOUNDS,$('#lat'),$('#lon'),'', [0,0]);
        });
        map.addLayer(first_marker_layer);
        map.on('locationfound', onLocationfound);
        interactive_form(onLocationfound, first_user_marker);
        map.locate();
        map.on('click', function (e) {
            var latlng = L.latLng(e.latlng.lat, e.latlng.lng);
            first_user_marker.setLatLng(latlng).update(first_user_marker);
            check_marker_position(e.latlng.lat, e.latlng.lng, first_user_marker, AEGEAN_BOUNDS,$('#lat'),$('#lon'),'', [0,0]);
        });
        tour_guide_senario_1();
    }

// });


    if(scenario === 3){
        lock = 1;
        first_user_marker = L.marker([38.06, 25.36], {draggable: true}).bindPopup("First Marker").addTo(map);

        first_marker_layer = L.layerGroup(first_user_marker);

        map.addLayer(first_marker_layer);


        $('#lat').val(38.06);
        $('#lon').val(25.36);

        var endpick = $('#enddatepicker').datetimepicker({
            autoclose: true,
            pickerPosition: 'top-left',

        });

        first_user_marker.on('dragend', function (e) {

            $('#lat').val(e.target._latlng.lat);
            $('#lon').val(e.target._latlng.lng);
            // let lat = e.latlng.lat;
            // let lon = e.latlng.lng;
            if (isInsideAegeanIonian(e.target._latlng.lat, e.target._latlng.lng)) {
                $("#sel1").val("202");
                $("#sel2").val("001");
            } else if (isInsideMediteranean(e.target._latlng.lat, e.target._latlng.lng)) {
                $("#sel1").val("201")
                $("#sel2").val("002")
            } else {
                alert("Point outside of Mediterranean sea. Please select another point");
                var latlng = L.latLng(38.06, 25.36);
                first_user_marker.setLatLng(latlng).update(first_user_marker);
                $('#lat').val(38.06);
                $('#lon').val(25.36);

            }
        });
        var third_scenario_tour = new Tour({
            storage: false,
            template: "<div class='popover tour' style='min-width: 350px; min-height: 120px; color: black;'>" +
                "<div class='arrow'></div>" +
                "<h3 class='popover-title' style='box-shadow: 0px 1px #bfbfbf;'></h3>" +
                "<div class='popover-content'></div>" +
                // "<div class='popover-navigation'>" +
                // "<button class='btn btn-sm btn-primary' data-role='prev'>« Prev</button>" +
                // "<span data-role='separator'>|</span>" +
                // "<button class='btn btn-sm btn-primary' data-role='next'>Next »</button>" +
                // "<button class='btn btn-sm btn-primary pull-right' data-role='end'>End tour</button>" +
                // "</div>" +
                "</div>",
        });
        third_scenario_tour.addStep({
            element: ".application-header",
            placement: "left",
            title: "Oil spill dispersion forecast",
            duration: 3500,
            content: "This scenario forecasts the dispersion of oilspil in a selected point on map. Fill in all the fields",
        });

        third_scenario_tour.addStep({
            element: ".oil-volume-container",
            placement: "left",
            title: "Oil volume input",
            content: "Insert the total amount of oil spilled in m3",
        });

        third_scenario_tour.init();
        third_scenario_tour.start(true);
    }


    var exec_instance = '';
    $("#run-service-btn").click(function () {
        if(parseInt(scenario) === 1)
            $("#execution_btn_OIL_SPILL_SCENARIO_1").click();
        else if(parseInt(scenario) === 2)
            $("#execution_btn_OIL_SPILL_SCENARIO_2").click();
        else if(parseInt(scenario) === 3)
            $("#execution_btn_OIL_SPILL_SCENARIO_3").click();

        var lat = $('#lat').val();
        var lng = $("#lon").val();
        var oil_volume = $("#oil_volume").val();
        var oil_density = $("#oil_density").val();
        var time_interval = $("#time_interval").val();
        var simulation_length = $("#simulation_length_hist").val();
        var duration = $("#vis_duration").val();
        lat2 = $('#lat2').val();
        lng2 = $('#lon2').val();
        lat3 = $('#lat3').val();
        lng3 = $('#lon3').val();
        if (isInsideMediteranean(lat, lng)  &&
            ((lat2 === "" || lng2 === "") || isInsideMediteranean(lat2, lng2)) &&
            ((lat3 === "" || lng3 === "") || isInsideMediteranean(lat3, lng3))) {
            lat4 = lng4 = lat5 = lng5 = ''
            start_date2 = $("#startdatepicker2 input").datepicker({dateFormat: "yy-mm-dd"}).val();
            start_date3 = $("#startdatepicker3 input").datepicker({dateFormat: "yy-mm-dd"}).val();
            start_date4 = start_date5 = ''
            duration2 = $("#vis_duration2").val();
            duration3 = $("#vis_duration3").val();
            duration4 = duration5 = '';
            var oil_volume2 = $("#oil_volume2").val();
            var oil_volume3 = $("#oil_volume3").val();
            var oil_volume4 = oil_volume5 = '';

            // var starting_date = new Date($("#startdatepicker input").val());
            // alert(starting_date);
            var start_date = $("#startdatepicker input").datepicker({dateFormat: "yy-mm-dd"}).val();
            var enddate = $("#enddatepicker input").datepicker({dateFormat: "yy-mm-dd"}).val();
            // var now = new Date();
            // alert(now);
            // var oneDay = 24*60*60*1000;
            // var diffDays = Math.round(Math.abs((starting_date.getTime() - now.getTime())/(oneDay)));
            // alert(diffDays);
            var wave_dataset = $("#sel1").val();
            var hd_dataset = $("#sel2").val();
            var natura_layer = $('input[name="natura_checkbox"]:checked').length > 0;
            var ais_layer = $('input[name="ais_checkbox"]:checked').length > 0;
            var url = "/oilspill/" +
                "scenario" + scenario +
                "/process/?" +
                "&latitude1=" + lat +
                "&longitude1=" + lng +
                "&start_date1=" + start_date +
                "&duration1=" + duration +
                "&latitude2=" + lat2 +
                "&longitude2=" + lng2 +
                "&start_date2=" + start_date2 +
                "&duration2=" + duration2 +
                "&latitude3=" + lat3 +
                "&longitude3=" + lng3 +
                "&start_date3=" + start_date3 +
                "&duration3=" + duration3 +
                "&latitude4=" + lat4 +
                "&longitude4=" + lng4 +
                "&start_date4=" + start_date4 +
                "&duration4=" + duration4 +
                "&latitude5=" + lat5 +
                "&longitude5=" + lng5 +
                "&start_date5=" + start_date5 +
                "&duration5=" + duration5 +
                "&end_date=" + enddate +
                "&oil_volume1=" + oil_volume +
                "&oil_volume2=" + oil_volume2 +
                "&oil_volume3=" + oil_volume3 +
                "&oil_volume4=" + oil_volume4 +
                "&oil_volume5=" + oil_volume5 +
                "&oil_density=" + oil_density +
                "&simulation_length=" + simulation_length +
                "&time_interval=" + time_interval +
                "&wave_model=" + wave_dataset +
                "&hd_model=" + hd_dataset +
                "&natura_layer=" + natura_layer +
                "&ais_layer=" + ais_layer;



            console.log(url);
            // window.location.replace(url);
            $("#execution_status").val('starting service');
            $.ajax({
                "type": "GET",
                "url": url,
                "data": {},
                "cache": false,
                "success": function(result) {
                        console.log(result);
                        exec_instance = result['exec_instance'];
                    },
                "error": function () {
                    set_execution_failed();
                }
            });

            var execution_status_interval = setInterval(check_execution_status, 3000);

            function check_execution_status() {
                $.ajax({
                    "type": "GET",
                    "url": "/oilspill/"+"scenario"+ scenario+"/status/"+exec_instance+"/",
                    "data": {},
                    "cache": false,
                    "success": function(result) {
                        console.log(result["status"]);
                        $("#execution_status").val(result["status"]);
                        if(result["status"] === "done"){
                            setTimeout(function() {
                                execution_status_stop();
                                window.location.href = "/oilspill/"+"scenario"+ scenario+"/results/"+exec_instance+"/";
                            }, 1000);
                        }
                        else if (result["status"] === "failed") {
                            execution_status_stop();
                            // alert("execution failed");
                        }
                    },
                    error: function () {
                        set_execution_failed();
                        execution_status_stop();
                        // alert('error');
                    }
                });
            }

            function execution_status_stop() {
                clearInterval(execution_status_interval);
            }

        }
        else {
            alert("Please select points inside Mediterranean sea")
        }
    });

    function set_execution_failed(){
        $(".modal.in .progress-bar").css({width: '100%', background: '#db2828'});
        $(".modal.in .status_counter").each(function (index, elem) {
            $(elem).removeClass('label-default').addClass('label-primary');
        });
        $(".modal.in #modal_dismiss_btn_cancel").hide();
        $(".modal.in #modal_dismiss_btn_close").show();
    }


    window.setInterval(function () {
        if($(".modal.in").length > 0) {
            var old_status = $(" .modal.in #modal_status_input").val();
            var new_status = $("#execution_status").val();
            if (old_status !== new_status) {
                console.log(new_status);
                $(".modal.in #modal_status_input").val(new_status);
                $(".modal.in #modal_status_div").fadeOut("2000").html(new_status).fadeIn("2000");
                $(".modal.in .status_counter").each(function (index, elem) {
                    console.log($(elem).data("status"));
                    if ($(elem).attr("data-status") === new_status) {
                        // console.log('found');
                        var new_step_counter = $(elem).attr("data-counter");
                        $(".modal.in .status_counter").each(function (i, e) {
                            if(i <= index){
                                $(e).removeClass('label-default').addClass('label-primary');
                            }
                        });

                        var $total = parseInt($(".modal.in #number_of_steps").val());
                        var $current = parseInt(new_step_counter);
                        var $percent = ($current / $total) * 100;
                        $(".modal.in .progress-bar").css({width: $percent + '%'});
                    }
                });

            }
            if (new_status === "failed"){
                set_execution_failed();
            }
        }
    }, 1000);

    $('.modal').on('hidden.bs.modal', function () {
        $(" .modal #modal_status_input").val('');
        $("#execution_status").val('');
        $(".modal #modal_dismiss_btn_cancel").show();
        $(".modal #modal_dismiss_btn_close").hide();
        $(".modal .status_counter").each(function (index, elem) {
            $(elem).removeClass('label-default').removeClass('label-primary').addClass('label-default');
        });
        $(".modal .progress-bar").css({width: '0%', background: '#337ab7'});
        $(".modal #modal_status_div").html('');
    });

    // $("#modal_dismiss_btn_cancel").click(function () {
    //     $.ajax({
    //         "type": "GET",
    //         "url": "/wave-energy/"+exec_instance+"/",
    //         "data": {},
    //         "success": function(result) {
    //             console.log('service cancelled');
    //         },
    //         error: function () {
    //             console.log('error cancelling service');
    //         },
    //         complete: function () {
    //             exec_instance = '';
    //         }
    //     });
    // });
    function map_init() {
        var maplayer = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token=';
        var token = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ';
        var attr = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors,' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>' +
        'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>';
        map = L.map('map').setView([38.41, 21.97], 4);
        L.tileLayer(maplayer + token, {
            attribution: attr,
            maxZoom: 18,
        }).addTo(map);
        init = true;
    }

    // function datetimepicker_initialisation(startDate, endDate){
    //     var startpick1 = $('#startdatepicker').datetimepicker({
    //         autoclose: true,
    //         pickerPosition: 'top-left',
    //         startDate: startDate,
    //         endDate: endDate,
    //         initialDate: endDate
    //     });
    //     startpick1.datetimepicker('update',endDate);
    //     var startpick2 = $('#startdatepicker2').datetimepicker({
    //         autoclose: true,
    //         pickerPosition: 'top-left',
    //         startDate: startDate,
    //         endDate: endDate,
    //         initialDate: endDate
    //     });
    //     startpick2.datetimepicker('update',endDate);
    //     var startpick3 = $('#startdatepicker3').datetimepicker({
    //         autoclose: true,
    //         pickerPosition: 'top-left',
    //         startDate: startDate,
    //         endDate: endDate,
    //         initialDate: endDate
    //     });
    //     startpick3.datetimepicker('update',endDate);
    //     var startpick4 = $('#startdatepicker4').datetimepicker({
    //         autoclose: true,
    //         pickerPosition: 'top-left',
    //         startDate: startDate,
    //         endDate: endDate,
    //         initialDate: endDate
    //     });
    //     startpick4.datetimepicker('update',endDate);
    //     var startpick5 = $('#startdatepicker5').datetimepicker({
    //         autoclose: true,
    //         pickerPosition: 'top-left',
    //         startDate: startDate,
    //         endDate: endDate,
    //         initialDate: endDate
    //     });
    //     startpick5.datetimepicker('update',endDate);
    //     return [startpick1,startpick2, startpick3, startpick4, startpick5]
    // }

    // function markers_initialisation() {
    //     second_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Oil-Spill-2");
    //     third_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Oil-Spill-3");
    //     fourth_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Oil-Spill-4");
    //     fifth_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Oil-Spill-5");
    //
    //     second_marker_layer = L.layerGroup(second_user_marker);
    //     third_marker_layer = L.layerGroup(third_user_marker);
    //     fourth_marker_layer = L.layerGroup(fourth_user_marker);
    //     fifth_marker_layer = L.layerGroup(fifth_user_marker);
    //
    //     map.addLayer(second_marker_layer);
    //     map.addLayer(third_marker_layer);
    //     map.addLayer(fourth_marker_layer);
    //     map.addLayer(fifth_marker_layer);
    //     return [second_user_marker, third_user_marker, fourth_user_marker, fifth_user_marker]
    // }

});