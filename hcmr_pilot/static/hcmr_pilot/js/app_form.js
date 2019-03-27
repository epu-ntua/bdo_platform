

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

let MAX_LON_MEDITERRANEAN = 36;
let MIN_LON_MEDITERRANEAN = -7;
let MAX_LAT_MEDITERRANEAN = 45.75;
let MIN_LAT_MEDITERRANEAN = 30.25;

let MAX_LON_AEGEAN_IONIAN = 30;
let MIN_LON_AEGEAN_IONIAN = 19.5;
let MAX_LAT_AEGEAN_IONIAN = 41;
let MIN_LAT_AEGEAN_IONIAN = 30.4;

function isInsideMediteranean(lat, lon) {
    return !((lat < MIN_LAT_MEDITERRANEAN || lat > MAX_LAT_MEDITERRANEAN) ||
        (lon < MIN_LON_MEDITERRANEAN || lon > MAX_LON_MEDITERRANEAN))
}

function isInsideAegeanIonian(lat, lon) {
    return !((lat < MIN_LAT_AEGEAN_IONIAN || lat > MAX_LAT_AEGEAN_IONIAN) ||
        (lon < MIN_LON_AEGEAN_IONIAN || lon > MAX_LON_AEGEAN_IONIAN))
}

function ckeck_markers_location() {
    area_bounds = areaSelect.getBounds();
    var swlat = Math.round(area_bounds.getSouthWest().lat * 10000) / 10000;
    var swlon = Math.round(area_bounds.getSouthWest().lng * 10000) / 10000;
    var nelat = Math.round(area_bounds.getNorthEast().lat * 10000) / 10000;
    var nelon = Math.round(area_bounds.getNorthEast().lng * 10000) / 10000;
    bounds = [swlat,swlon,nelat,nelon];
    var latlng1
    var latlng1
    var latlng1
    var latlng1
}

function create_new_area_select(area_select_bounds){
    $(".leaflet-interactive").remove();
    areaSelect = L.rectangle(area_select_bounds);
    map.addLayer(areaSelect);
    areaSelect.editing.enable();
    area_bounds = areaSelect.getBounds();
    areaSelect.on("edit", function() {
        area_bounds = this.getBounds();
    });
    // map.fitBounds(area_select_bounds);
    bounds = [area_select_bounds[0][0],area_select_bounds[0][1],area_select_bounds[1][0],area_select_bounds[1][1]];
    $('#lat_min').val(bounds[0]);
    $('#lat_max').val(bounds[2]);
    $('#lon_min').val(bounds[1]);
    $('#lon_max').val(bounds[3]);

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
        element: ".time-interval-container",
        placement: "left",
        title: "Time interval",
        content: "Set the time step of the output results.",
    });
    first_scenario_tour.addStep({
        element: ".simulation-length-container",
        placement: "left",
        title: "Simulation length",
        content: "Set the duration of the requested simulation in hours (30 days maximum length).",
    });

    first_scenario_tour.addStep({
        element: ".oil-density-container",
        placement: "left",
        title: "Oil density",
        content: "Set the density of oil spilled in the sea in kg/ m3.",
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

function check_marker_position(lat, lon, user_marker){
    if (isInsideAegeanIonian(lat,lon)) {
        $("#sel1").dropdown("set selected", "202");
        $("#sel2").dropdown("set selected", "001");
        $('#lat').val(lat.toFixed(4));
        $('#lon').val(lon.toFixed(4));
    } else if (isInsideMediteranean(lat,lon)) {
        $("#sel1").dropdown("set selected", "201");
        $("#sel2").dropdown("set selected", "002");
        $('#lat').val(lat.toFixed(4));
        $('#lon').val(lon.toFixed(4));
    } else {
        alert("Point outside of Mediterranean sea. Please select another point");
        var latlng = L.latLng(38.06, 25.36);
        user_marker.setLatLng(latlng).update(user_marker);
        $('#lat').val((38.06).toFixed(4));
        $('#lon').val((25.36).toFixed(4));
    }
};

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
            if (ist > diff_dec_days*24){
                $(this).addClass('disabled');
            }
            console.log(ist)
        });

    }

}

function interactive_form(onLocationfound){
    var allow_form_submit = [true, true, true, true, true, true];
    check_sim_len_options();
    $('#lat').on('input',function () {
        allow_form_submit = missing_parameter($('#lat'), allow_form_submit, 'latitude', 0);
        if($('#lat').val()<-90){
            $('#lat').val((-90).toFixed(4));
        }else if($('#lat').val()>90){
            $('#lat').val((90).toFixed(4));
        }
        onLocationfound({latlng:[$('#lat').val(),$('#lon').val()]});
    });
    $('#lon').on('input',function () {
        allow_form_submit = missing_parameter($('#lon'), allow_form_submit, 'longitude', 1);
        if($('#lon').val()<-180){
            $('#lon').val((-180).toFixed(4));
        }else if($('#lon').val()>180){
            $('#lon').val((180).toFixed(4));
        }
        onLocationfound({latlng:[$('#lat').val(),$('#lon').val()]});
    });
    $('#startdatepicker input').on('change',function () {
        allow_form_submit = missing_parameter($('#startdatepicker input'), allow_form_submit, 'date', 2);
        check_sim_len_options();
    });
    $('#startdatepicker input').on('input',function () {
        allow_form_submit = missing_parameter($('#startdatepicker input'), allow_form_submit, 'date', 2);
        check_sim_len_options();
    });
    $('#oil_volume').on('input',function(){
        allow_form_submit = missing_parameter($('#oil_volume'), allow_form_submit, 'oil-volume', 3);
        if ($('#oil_volume').val()<0){
            $('#oil_volume').val(0);
        }
    });
    $('#oil_density').on('input',function(){
        allow_form_submit = missing_parameter($('#oil_density'), allow_form_submit, 'oil-density', 4);
        if ($('#oil_density').val()<0){
            $('#oil_density').val(0);
        }
    });
    $('#vis_duration').on('input',function(){
        allow_form_submit = missing_parameter($('#vis_duration'), allow_form_submit, 'duration', 5);
        if ($('#vis_duration').val()<0){
            $('#vis_duration').val(0);
        }
    });
    $('#simulation_length_hist').on('change',function(){
        var starting_date = new Date($("#startdatepicker input").val());
        var now = new Date();
        var oneDay = 24*60*60*1000;
        var diffDays = Math.round(Math.abs((starting_date.getTime() - now.getTime())/(oneDay)));
        var selected_length = $(this).val()/24;
        if(selected_length<=diffDays){
            $('#simulation_length').parent().addClass('disabled')
        }else if($('#simulation_length_hist').val()>diffDays) {
            $('#simulation_length_hist').val(diffDays);
            $('#simulation_length').parent().removeClass('disabled')
            var days_allowed = 30 - diffDays
            if(days_allowed === 1){
                $('#simulation_length').parent().find('div[data-value=36]').addClass('disabled');
                $('#simulation_length').parent().find('div[data-value=48]').addClass('disabled');
                $('#simulation_length').parent().find('div[data-value=60]').addClass('disabled');
                $('#simulation_length').parent().find('div[data-value=72]').addClass('disabled');
                $('#simulation_length').parent().find('div[data-value=84]').addClass('disabled');
                $('#simulation_length').parent().find('div[data-value=96]').addClass('disabled');
            }else if(days_allowed === 2){
                $('#simulation_length').parent().find('div[data-value=60]').addClass('disabled');
                $('#simulation_length').parent().find('div[data-value=72]').addClass('disabled');
                $('#simulation_length').parent().find('div[data-value=84]').addClass('disabled');
                $('#simulation_length').parent().find('div[data-value=96]').addClass('disabled');
            }else if(days_allowed === 3){
                $('#simulation_length').parent().find('div[data-value=84]').addClass('disabled');
                $('#simulation_length').parent().find('div[data-value=96]').addClass('disabled');
            }

        }else if ($('#simulation_length_hist').val()>1330){
            $('#simulation_length_hist').val(30);
        }

    });
}

function missing_parameter(col_select, allow_submit, parameter_name, parameter_id) {
    if ((col_select.val() === null) || (col_select.val().length === 0)) {
        if (allow_submit[parameter_id] === true) {
            $('#run-service-btn').addClass('disabled');
            $("<div class='conf-error-message " + parameter_name + "_missing_error'>* Selection of " + parameter_name + " is required.</div>").insertBefore("#run-service-btn");
        }
        allow_submit[parameter_id] = false;
    }
    else {
        allow_submit[parameter_id] = true;
        $('.' + parameter_name + '_missing_error').remove();
        if (check_list(allow_submit)) {
            $('#run-service-btn').removeClass('disabled');
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

$(document).ready(function() {
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
    var startpick = $('#startdatepicker').datetimepicker({
        autoclose: true,
        pickerPosition: 'bottom-left',
        startDate: startDate,
        endDate: endDate,
        initialDate: endDate
    });
    startpick.datetimepicker('update',endDate);

    var allow_form_submit = [true, true, true, true, true, true];

    if(scenario === 2){

        var second_scenario_tour = new Tour({
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

        second_scenario_tour.addStep({
            element: ".spatial-selection",
            placement: "left",
            title: "Area selection",
            content: "Adjust the blue rectangle to the area you wih to investigate. When you finish press the lock area button to lock the coordinates",
        });

        second_scenario_tour.init();
        second_scenario_tour.start(true);

        create_new_area_select([[29.2575,-15.2578],[49.479,42.0898]]);

        var startpick2 = $('#startdatepicker2').datetimepicker({
            autoclose: true,
            pickerPosition: 'top-left',

        });

        var startpick3 = $('#startdatepicker3').datetimepicker({
            autoclose: true,
            pickerPosition: 'top-left',

        });

        second_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Second Marker");
        third_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Third Marker");
        fourth_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Fourth Marker");
        fifth_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Fifth Marker");

        second_marker_layer = L.layerGroup(second_user_marker);
        third_marker_layer = L.layerGroup(third_user_marker);
        fourth_marker_layer = L.layerGroup(fourth_user_marker);
        fifth_marker_layer = L.layerGroup(fifth_user_marker);

        map.addLayer(second_marker_layer);
        map.addLayer(third_marker_layer);
        map.addLayer(fourth_marker_layer);
        map.addLayer(fifth_marker_layer);
    }



    if (scenario === 1) {
        $('#lat').val((38.06).toFixed(4));
        $('#lon').val((25.36).toFixed(4));
        first_user_marker = L.marker([38.06, 25.36], {draggable: true}).bindPopup("First Marker").addTo(map);
        first_marker_layer = L.layerGroup(first_user_marker);
        onLocationfound = function(e){
            first_user_marker.setLatLng(e.latlng).update();
        };
        first_user_marker.on('dragend', function (e) {
            check_marker_position(e.target._latlng.lat, e.target._latlng.lng,first_user_marker);
        });
        map.addLayer(first_marker_layer);
        map.on('locationfound', onLocationfound);
        interactive_form(onLocationfound);
        map.locate();
        map.on('click', function (e) {
            if (first_user_marker != undefined) {
                map.removeLayer(first_user_marker);
            }
            first_user_marker = L.marker([e.latlng.lat, e.latlng.lng], {draggable: true}).bindPopup("First Marker").addTo(map);
            first_marker_layer = L.layerGroup(first_user_marker);
            map.addLayer(first_marker_layer);
            check_marker_position(e.latlng.lat, e.latlng.lng, first_user_marker);
            first_user_marker.on('dragend', function (e) {
                check_marker_position(e.target._latlng.lat, e.target._latlng.lng, first_user_marker);
            });
        });
        tour_guide_senario_1();
    }

    $('.oil-volume-container').change(function () {
        // if(scenario === 1) {
        //     if (first_scenario_tour.getCurrentStep() === 2) {
        //         // first_scenario_tour.addStep({
        //         //     element: ".vis-duration-container",
        //         //     placement: "left",
        //         //     title: "Simulation duration",
        //         //     content: "Duration of the spill release in hours",
        //         // });
        //         first_scenario_tour.next();
        //     } else {
        //         first_scenario_tour.setCurrentStep(7);
        //     }
        // }
        // else {
        //     if (third_scenario_tour.getCurrentStep() === 1) {
        //         third_scenario_tour.addStep({
        //             element: ".vis-duration-container",
        //             placement: "left",
        //             title: "Simulation duration",
        //             content: "Duration of the spill release in hours",
        //         });
        //         third_scenario_tour.next();
        //     } else {
        //         third_scenario_tour.setCurrentStep(7);
        //     }
        // }
    });

    $('.vis-duration-container').change(function () {
        // if (scenario  === 1) {
        //     if (first_scenario_tour.getCurrentStep() === 3) {
        //         // first_scenario_tour.addStep({
        //         //     element: ".time-interval-container",
        //         //     placement: "left",
        //         //     title: "Time interval",
        //         //     content: "Time interval between two outputs in hours",
        //         // });
        //         first_scenario_tour.next();
        //     } else {
        //         first_scenario_tour.setCurrentStep(7);
        //     }
        // }
        // else{
        //     if(third_scenario_tour.getCurrentStep() === 2){
        //         third_scenario_tour.addStep({
        //             element: ".time-interval-container",
        //             placement: "left",
        //             title: "Time interval",
        //             content: "Time interval between two outputs in hours",
        //         });
        //         third_scenario_tour.next();
        //     }
        //     else{
        //         third_scenario_tour.setCurrentStep(7);
        //     }
        // }
    });

    $('.time-interval-container').change(function () {
        // if (scenario  === 1){
        //     if (first_scenario_tour.getCurrentStep() === 4) {
        //         // first_scenario_tour.addStep({
        //         //     element: ".simulation-length-container",
        //         //     placement: "left",
        //         //     title: "Simulation length",
        //         //     content: "Length of the requested simulation in hours ( max 30 days)",
        //         // });
        //         first_scenario_tour.next();
        //     } else {
        //         first_scenario_tour.setCurrentStep(7);
        //     }
        // }
        // else {
        //     if (third_scenario_tour.getCurrentStep() === 3) {
        //         third_scenario_tour.addStep({
        //             element: ".simulation-length-container",
        //             placement: "left",
        //             title: "Simulation length",
        //             content: "Length of the requested simulation in hours ( max 30 days)",
        //         });
        //         third_scenario_tour.next();
        //     } else {
        //         third_scenario_tour.setCurrentStep(7);
        //     }
        // }
    });

    $('.simulation-length-container').change(function () {
        // if (scenario === 1) {
        //     if (first_scenario_tour.getCurrentStep() === 5) {
        //         // first_scenario_tour.addStep({
        //         //     element: ".oil-density-container",
        //         //     placement: "left",
        //         //     title: "Oil density",
        //         //     content: "Density of oil (kg/m3)",
        //         // });
        //         first_scenario_tour.next();
        //     } else {
        //         first_scenario_tour.setCurrentStep(7);
        //     }
        // }
        // else {
        //     if (third_scenario_tour.getCurrentStep() === 4) {
        //         third_scenario_tour.addStep({
        //             element: ".oil-density-container",
        //             placement: "left",
        //             title: "Oil density",
        //             content: "Density of oil (kg/m3)",
        //         });
        //         third_scenario_tour.next();
        //     } else {
        //         third_scenario_tour.setCurrentStep(7);
        //     }
        // }
    });

    $('.oil-density-container').change(function () {
        // if(scenario === 1) {
        //     if (first_scenario_tour.getCurrentStep() === 6) {
        //         //  first_scenario_tour.addStep({
        //         //     element: ".dataset-selector",
        //         //     placement: "left",
        //         //     title: "Model Selection",
        //         //     duration: 3500,
        //         //     content: "The selected models depend on the location of the marker. The supported area is the Mediterranean sea",
        //         // });
        //         // first_scenario_tour.addStep({
        //         //     element: ".checkbox",
        //         //     placement: "left",
        //         //     title: "Additional layers",
        //         //     duration: 3500,
        //         //     content: "Insert an additional layers to the simulation. If you do not wish select None!",
        //         // });
        //         //
        //         // first_scenario_tour.addStep({
        //         //     element: ".service-buttons",
        //         //     placement: "left",
        //         //     title: "Execution",
        //         //     duration: 3500,
        //         //     content: "All set. Ready to execute!",
        //         // });
        //         first_scenario_tour.next();
        //     } else {
        //         first_scenario_tour.setCurrentStep(7);
        //     }
        // }
        // else {
        //     if (third_scenario_tour.getCurrentStep() === 5) {
        //         third_scenario_tour.addStep({
        //             element: ".vis-startdate-container",
        //             placement: "left",
        //             title: "Datetime Selection",
        //             content: "Date and time start",
        //         });
        //         third_scenario_tour.next();
        //     }
        //     else {
        //         third_scenario_tour.setCurrentStep(7);
        //     }
        // }
    });

    $('.vis-startdate-container').change(function () {
        // if (scenario === 1) {
        //     if (first_scenario_tour.getCurrentStep() === 1) {
        //         // first_scenario_tour.addStep({
        //         //     element: ".oil-volume-container",
        //         //     placement: "left",
        //         //     title: "Oil volume input",
        //         //     content: "Insert the total amount of oil spilled in m3",
        //         // });
        //         first_scenario_tour.next();
        //     } else {
        //         first_scenario_tour.setCurrentStep(7);
        //     }
        // }
        // else{
        //    if (third_scenario_tour.getCurrentStep() === 6) {
        //         third_scenario_tour.addStep({
        //             element: ".service-buttons",
        //             placement: "left",
        //             title: "Execution",
        //             duration: 3500,
        //             content: "All set. Ready to execute!"
        //         });
        //         third_scenario_tour.next();
        //     }
        //     else {
        //         third_scenario_tour.setCurrentStep(7);
        //     }
        // }
    });


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

    $('#lock_area').on('click', function(e){

        lock = 1;

        areaSelect.editing.disable();

        $('.spatial-selection').hide();
        $('.points-container').show();
        $('.service-buttons').show();
        $('#unlock-area').show();
         // $('.lock-button').hide();
        area_bounds = areaSelect.getBounds();
        var swlat = Math.round(area_bounds.getSouthWest().lat * 10000) / 10000;
        var swlon = Math.round(area_bounds.getSouthWest().lng * 10000) / 10000;
        var nelat = Math.round(area_bounds.getNorthEast().lat * 10000) / 10000;
        var nelon = Math.round(area_bounds.getNorthEast().lng * 10000) / 10000;
        bounds = [swlat,swlon,nelat,nelon];
        $('#lat_min').val(bounds[0]);
        $('#lat_max').val(bounds[2]);
        $('#lon_min').val(bounds[1]);
        $('#lon_max').val(bounds[3]);
        first_user_marker = L.marker([(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2], {draggable: true}).bindPopup("First Marker").addTo(map);
        first_marker_layer = L.layerGroup(first_user_marker);
        map.addLayer(first_marker_layer);
        $('#lat').val((bounds[0] + bounds[2]) / 2);
        $('#lon').val((bounds[1] + bounds[3]) / 2);
        map.setView([(bounds[0] + bounds[2]) / 2,(bounds[1] + bounds[3]) / 2], 9);

        second_scenario_tour.addStep({
            element: ".points-container",
            placement: "left",
            title: "Simulations Points",
            duration: 6000,
            content: "Once you selected the area, select more specifically the points within the selected area. " +
                "The simulation supports up to five points. Feel free to select whatever number of points. " +
                "All the simulation points must be placed inside the selected area otherwise the simulation can not be executed. " +
                "You can go back to edit the location of the selected area",
        });
        second_scenario_tour.addStep({
            element: ".service-parameters",
            placement: "left",
            title: "Service parameters",
            duration: 3500,
            content: "These parameters are common for all the points of the simulation. Time interval is measured in hours, " +
                "simulation length in hours (max 30 days) and oil density in kg/m3 ",
        });
        second_scenario_tour.next();

    });

    $('#unlock-area').on('click', function(e){
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



    // map.on('click', function (e) {
    //     if(lock === 1) {
    //         if (first_user_marker != undefined) {
    //             map.removeLayer(first_user_marker);
    //         }
    //
    //         first_user_marker = L.marker([e.latlng.lat, e.latlng.lng], {draggable: true}).bindPopup("First Marker").addTo(map);
    //         first_marker_layer = L.layerGroup(first_user_marker);
    //         map.addLayer(first_marker_layer);
    //         let lat = e.latlng.lat;
    //         let lon = e.latlng.lng;
    //         if (isInsideAegeanIonian(lat, lon)) {
    //             $("#sel1").val("202");
    //             $("#sel2").val("001");
    //         } else if (isInsideMediteranean(lat, lon)) {
    //             $("#sel1").val("201")
    //             $("#sel2").val("002")
    //         } else {
    //             alert("Point outside of Mediterranean sea. Please select another point");
    //             if (first_user_marker != undefined) {
    //                 map.removeLayer(first_user_marker);
    //             }
    //             first_user_marker = L.marker([38.06, 25.36], {draggable: true}).bindPopup("First Marker").addTo(map);
    //
    //             first_marker_layer = L.layerGroup(first_user_marker);
    //
    //             map.addLayer(first_marker_layer);
    //             $('#lat').val(38.06);
    //             $('#lon').val(25.36);
    //
    //         }
    //
    //         $('#lat').val(e.latlng.lat);
    //         $('#lon').val(e.latlng.lng);
    //         first_user_marker.on('dragend', function (e) {
    //
    //             $('#lat').val(e.target._latlng.lat);
    //             $('#lon').val(e.target._latlng.lng);
    //         });
    //
    //     }
    // });



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
        area_bounds = areaSelect.getBounds();
        var swlat = Math.round(area_bounds.getSouthWest().lat * 10000) / 10000;
        var swlon = Math.round(area_bounds.getSouthWest().lng * 10000) / 10000;
        var nelat = Math.round(area_bounds.getNorthEast().lat * 10000) / 10000;
        var nelon = Math.round(area_bounds.getNorthEast().lng * 10000) / 10000;
        var x_mov = 3*(nelat - swlat) / swlat;
        var y_mov = 3*(nelon - swlon) / swlon;
        bounds = [swlat,swlon,nelat,nelon];

        if ( tabid2 === "#point2_form"){

            if (second_user_marker != undefined) {
                map.removeLayer(second_user_marker);
            }
            var startpick = $('#startdatepicker2').datetimepicker({
                autoclose: true,
                pickerPosition: 'top-left',

            });
            var redIcon = new L.Icon({
                iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'
            });
            second_user_marker = L.marker([((bounds[0] + bounds[2] ) / 2) - x_mov, ((bounds[1] + bounds[3] ) / 2) - y_mov], {draggable:true}, {icon: redIcon}).bindPopup("Second Marker").addTo(map);
            second_user_marker.setIcon(redIcon);
            second_marker_layer = L.layerGroup(second_user_marker);
            map.addLayer(second_marker_layer);
            second_user_marker.on('dragend', function (e) {

                $('#lat2').val(e.target._latlng.lat);
                $('#lon2').val(e.target._latlng.lng);
            });
            var lat = ((bounds[0] + bounds[2] ) / 2) - 0.1;
            var lng = ((bounds[1] + bounds[3] ) / 2) - 0.1;
            $('#lat2').val(lat);
            $('#lon2').val(lng);
        }
        else if(tabid2 === "#point3_form"){
            var startpick = $('#startdatepicker3').datetimepicker({
                autoclose: true,
                pickerPosition: 'top-left',

            });
            if (third_user_marker != undefined) {
                map.removeLayer(third_user_marker);
            }
            var greenIcon = new L.Icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png'
            });
            third_user_marker = L.marker([((bounds[0] + bounds[2]) / 2) - x_mov, ((bounds[1] + bounds[3] ) / 2) + y_mov ], {draggable:true}, {icon: greenIcon}).bindPopup("Third Marker").addTo(map);
            third_user_marker.setIcon(greenIcon);
            third_marker_layer = L.layerGroup(third_user_marker);
            map.addLayer(third_marker_layer);

            third_user_marker.on('dragend', function (e) {
                $('#lat3').val(e.target._latlng.lat);
                $('#lon3').val(e.target._latlng.lng);
            });
            var lat = ((bounds[0] + bounds[2] ) / 2) - 0.1;
            var lng = ((bounds[1] + bounds[3] ) / 2) + 0.1;
            $('#lat3').val(lat);
            $('#lon3').val(lng);

        }
        else if (tabid2 === "#point4_form"){
            var startpick = $('#startdatepicker4').datetimepicker({
                autoclose: true,
                pickerPosition: 'top-left',

            });
            if (fourth_user_marker != undefined) {
                map.removeLayer(fourth_user_marker);
            }
            var orangeIcon = new L.Icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png'
            });
            fourth_user_marker = L.marker([((bounds[0] + bounds[2] ) / 2) + x_mov, ((bounds[1] + bounds[3]) / 2) - y_mov], {draggable:true}, {icon: greenIcon}).bindPopup("Fourth Marker").addTo(map);
            fourth_user_marker.setIcon(orangeIcon);
            fourth_marker_layer = L.layerGroup(fourth_user_marker);
            map.addLayer(fourth_marker_layer);

            fourth_user_marker.on('dragend', function (e) {
                $('#lat4').val(e.target._latlng.lat);
                $('#lon4').val(e.target._latlng.lng);
            });
            var lat = ((bounds[0] + bounds[2] ) / 2) + 0.1;
            var lng = ((bounds[1] + bounds[3] ) / 2) - 0.1;
            $('#lat4').val(lat);
            $('#lon4').val(lng);
        }
        else if (tabid2 === "#point5_form"){
            var startpick = $('#startdatepicker5').datetimepicker({
                autoclose: true,
                pickerPosition: 'top-left',

            });
            if (fifth_user_marker != undefined) {
                map.removeLayer(fifth_user_marker);
            }
            var blackIcon = new L.Icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-black.png'
            });
            fifth_user_marker = L.marker([((bounds[0] + bounds[2] ) / 2) + x_mov, ((bounds[1] + bounds[3] ) / 2) + y_mov], {draggable:true}, {icon: greenIcon}).bindPopup("Fourth Marker").addTo(map);
            fifth_user_marker.setIcon(blackIcon);
            fifth_marker_layer = L.layerGroup(fifth_user_marker);
            map.addLayer(fifth_marker_layer);

            fifth_user_marker.on('dragend', function (e) {
                $('#lat5').val(e.target._latlng.lat);
                $('#lon5').val(e.target._latlng.lng);
            });
            var lat = ((bounds[0] + bounds[2] ) / 2) + 0.1;
            var lng = ((bounds[1] + bounds[3] ) / 2) + 0.1;
            $('#lat5').val(lat);
            $('#lon5').val(lng);
        }

    });

    $('#remove_point2').click(function () {
        $('#lat2').val("");
        $('#lon2').val("");
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
        $('#lat3').val("");
        $('#lon3').val("");
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
        $('#lat4').val("");
        $('#lon4').val("");
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
        $('#lat5').val("");
        $('#lon5').val("");
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

});