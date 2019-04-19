
var single_marker_layer;
var user_marker = {};
var mode='location';

$(document).ready(function() {

    $('#select_app').dropdown();
    $('#select_dataset').dropdown();
    $('.ui.dropdown').dropdown();


    function set_forecast_timeframe(){
         var startDate = new  Date();
         startDate.setDate(startDate.getDate() + 1);
         startDate.setHours(0,0,0,0);
         var startpick = $('#startdatepicker').datetimepicker({
             autoclose: true,
             pickerPosition: 'top-left',
             startDate: startDate,
             endDate: startDate,
         });
         $('#startdatepicker').datetimepicker("update", startDate);
         $('#startdatepicker').datetimepicker('setStartDate', startDate);
         $('#startdatepicker').datetimepicker('setEndDate', startDate);

         var endDate = new  Date();
         endDate.setDate(endDate.getDate() + 7);
         endDate.setHours(23,59,59,999);
         var endpick = $('#enddatepicker').datetimepicker({
             autoclose: true,
             pickerPosition: 'top-left',
             startDate: endDate,
             endDate: endDate,
         });
         $('#enddatepicker').datetimepicker("update", endDate);
         $('#enddatepicker').datetimepicker('setStartDate', endDate);
         $('#enddatepicker').datetimepicker('setEndDate', endDate);
    }

    var tour = new Tour({
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

    tour.addStep({
        element: ".app-selector",
        placement: "left",
        title: "Application selection",
        content: "Please select the application for use",
    });

    // tour.init();
    //
    // tour.start(true);

    var wecs_location_assessment_tour = new Tour({
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
    // wecs_location_assessment_tour.init();

    var wec_assessment_area_tour = new Tour({
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
    // wec_assessment_area_tour.init();

    var wec_energy_generation_forecast_tour = new Tour({
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
    // wec_energy_generation_forecast_tour.init();

    var matching_analysis_tour = new Tour({
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
    // matching_analysis_tour.init();

    function create_new_area_select(area_select_bounds){
        $(".leaflet-interactive").remove();
        areaSelect = L.rectangle(area_select_bounds);
        map.addLayer(areaSelect);
        areaSelect.editing.enable();
        area_bounds = areaSelect.getBounds();
        areaSelect.on("edit", function() {
                area_bounds = this.getBounds();
            });
        map.fitBounds(area_select_bounds);
        bounds = [area_select_bounds[0][0],area_select_bounds[0][1],area_select_bounds[1][0],area_select_bounds[1][1]];
        $('#lat_min').val(bounds[0]);
        $('#lat_max').val(bounds[2]);
        $('#lon_min').val(bounds[1]);
        $('#lon_max').val(bounds[3]);

    }

    function removeAreaSelect() {
        var layers_arr = Object.values(map._layers);
        layers_arr.shift();
        $.each(layers_arr, function(i, e){e.remove()});
    }

    function set_app_dataset_date_pickers(app_selector) {
       $('#'+app_selector).change(function () {

           var dataset_id = $('#'+app_selector+" :selected").val();

            if(dataset_id === ""){
                $('#startdatepicker').find("input[type=text], textarea").val("").val('');
                $('#enddatepicker').find("input[type=text], textarea").val("").val('');
            }
            else{
                var startdate = new Date($('#'+app_selector+" :selected").data("startdate"));
                var enddate = new Date($('#'+app_selector+" :selected").data("enddate"));

                var startpick = $('#startdatepicker').datetimepicker({
                    autoclose: true,
                    pickerPosition: 'top-left',
                    startDate: startdate,
                    endDate: enddate,
                });
                $('#startdatepicker').datetimepicker("update", startdate);

                var endpick = $('#enddatepicker').datetimepicker({
                    autoclose: true,
                    pickerPosition: 'top-left',
                    startDate: startdate,
                    endDate: enddate,
                });
                $('#enddatepicker').datetimepicker("update", enddate);
            }
       });
        if($('.app-selector :selected').val() === "3")
            set_forecast_timeframe();
   }

    $(function () {
        $(".wecs_assessment_location_dropdown").change(function () {
               wecs_location_assessment_tour.addSteps([
                {
                    element: ".coverage-date-filters",
                    placement: "left",
                    title: "Service timeframe",
                    duration: 3500,
                    content: "Select the timeframe you wish to run the service. By default, minimum and maximum values of the dataset are selected",
                },
                {
                    element: ".converters-container",
                    placement: "left",
                    title: "Wave energy converter selection",
                    content: "Select at least one converter to execute your evaluation",
                },
                {
                    element: "#run-service-btn",
                    placement: "left",
                    duration: 3000,
                    title: "Service Execution",
                    content: "Ready to execute!",

                }]);
                wecs_location_assessment_tour.next();
        })
    });

     $(function () {
        $(".matching_analysis_dropdown").change(function () {
               matching_analysis_tour.addSteps([
                {
                    element: ".coverage-date-filters",
                    placement: "left",
                    title: "Service timeframe",
                    duration: 3500,
                    content: "Select the timeframe you wish to run the service. By default, minimum and maximum values of the dataset are selected",
                },
                {
                    element: ".radio-container",
                    placement: "left",
                    title: "Wave energy converter selection",
                    content: "Select at least one converter to execute your evaluation",
                },
                {
                    element: "#run-service-btn",
                    placement: "left",
                    duration: 3000,
                    title: "Service Execution",
                    content: "Ready to execute!",

                }]);
                matching_analysis_tour.next();
        })
    });
    
    $(function () {
        $(".converters-container").change(function () {
            if(wecs_location_assessment_tour.getCurrentStep() === 3 ){
                wecs_location_assessment_tour.addSteps([
                {
                    element: "#run-service-btn",
                    placement: "left",
                    duration: 3000,
                    title: "Service Execution",
                    content: "Ready to execute!",

                }]);
                wecs_location_assessment_tour.next();
            }
        })
    });

    $(function () {
        $(".radio-container").change(function () {

            if($('.app-selector :selected').val() === "2") {
                if(wec_assessment_area_tour.getCurrentStep() === 1) {
                    wec_assessment_area_tour.addSteps([
                        {
                            element: "#run-service-btn",
                            placement: "left",
                            duration: 3000,
                            title: "Service Execution",
                            content: "Ready to execute!",

                        }]);
                    wec_assessment_area_tour.next();
                }
                else
                    wec_assessment_area_tour.end();
            }
            else if($('.app-selector :selected').val() === "3") {
                if(wec_energy_generation_forecast_tour.getCurrentStep() === 1) {
                    wec_energy_generation_forecast_tour.addSteps([
                        {
                            element: "#run-service-btn",
                            placement: "left",
                            duration: 3000,
                            title: "Service Execution",
                            content: "Ready to execute!",

                        }]);
                    wec_energy_generation_forecast_tour.next();
                }
                else
                    wec_energy_generation_forecast_tour.end();
            }
            else if($('.app-selector :selected').val() === "4"){
                if (matching_analysis_tour.getCurrentStep() === 3) {
                    matching_analysis_tour.addSteps([
                        {
                            element: "#run-service-btn",
                            placement: "left",
                            duration: 3000,
                            title: "Service Execution",
                            content: "Ready to execute!",

                        }]);
                    matching_analysis_tour.next();
                }
                else
                   matching_analysis_tour.end();
            }
        })
    });

    $(function () {
        $('.app-selector').change(function () {
            if($('.app-selector :selected').val() === "1"){
                $('.single-spatial-selection').show();
                $('.dataset-selector').show();
                $(".wecs_assessment_location_dropdown").show();
                $('.coverage-date-filters').show();
                $(".run-service-button-container").show();
                $('.converters-container').show();



                wecs_location_assessment_tour.addStep(
                {
                    element: ".single-spatial-selection",
                    placement: "left",
                    title: "Geographic selection",
                    content: "Click on the map to place your marker or manually set your coordinates",
                });
                wecs_location_assessment_tour.start(true);
                wecs_location_assessment_tour.next();

                map.on('click', function(e){
                    if (mode == "location") {
                        $('#lat').val(e.latlng.lat);
                        $('#lon').val(e.latlng.lng);

                        $('.dataset-selector').show();

                        $(".item").each(function() {
                            if($(this).hasClass("disabled")) {
                                $(this).removeClass("disabled");
                            }
                        });

                        $('#wecs_assessment_location_dropdown  option').each(function () {
                            if($(this).data("maxlat") < e.latlng.lat || $(this).data("minlat") > e.latlng.lat || $(this).data("minlng") > e.latlng.lng || $(this).data("maxlng") < e.latlng.lng){
                                var dropdown_id = $(this).val();
                                $(`.item[data-value="${dropdown_id}"]`).addClass("disabled");
                            }
                        });

                        if (user_marker != undefined) {
                            map.removeLayer(user_marker);
                        }

                        user_marker = L.marker([e.latlng.lat, e.latlng.lng], {draggable:true}).bindPopup("AS4254").addTo(map);
                        single_marker_layer = L.layerGroup(user_marker);
                        map.addLayer(single_marker_layer);
                        user_marker.on('dragend', function (e) {
                            // alert(e.target._latlng);
                             $('#lat').val(e.target._latlng.lat);
                             $('#lon').val(e.target._latlng.lng);
                        });
                        if(wecs_location_assessment_tour.getCurrentStep()	 == 0){
                            wecs_location_assessment_tour.addStep({
                                element: ".dataset-selector",
                                placement: "left",
                                title: "Dataset selection",
                                content: "Dataset selection for application's execution",
                            });
                            wecs_location_assessment_tour.next();
                        }

                    }
                });
                set_app_dataset_date_pickers("select_dataset_wecs_assessment_location");
            }
            else{
                // $('#startdatepicker input').val('');
                // $('#enddatepicker input').val('');
                $('#lat').val('');
                $('#lon').val('');
                $('.single-spatial-selection').hide();
                $('.dataset-selector').hide();
                $(".wecs_assessment_location_dropdown").hide();
                $('.coverage-date-filters').hide();
                $('.converters-container').hide();

            }
            if($('.app-selector :selected').val() === "2"){
                mode = "area";
                $("#map").css("cursor", "grab");
                $('.spatial-selection').show();
                $(".run-service-button-container").show();
                $('.radio-container').show();
                create_new_area_select([[29.2575,-24.2578],[49.479,37.0898]]);
                $('.leaflet-edit-move').mouseup(function(){
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
                });

                $('.leaflet-edit-resize').mouseup(function(){
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
                });
                wec_assessment_area_tour.start(true);
                wec_assessment_area_tour.addSteps([
                    {
                        element: ".spatial-selection",
                        placement: "left",
                        title: "Geographic selection",
                        duration: 3000,
                        content: "Move the blue area to select the area you wish to execute your service",
                    },
                    {
                        element: ".radio-container",
                        placement: "left",
                        title: "Wave energy converter selection",
                        content: "Select the converter for your simulation. You can select only one",
                    }
                ]);
                wec_assessment_area_tour.start(true);

            }
            else{
                mode = "location";
                $("#map").css("cursor", "pointer");
                $('.spatial-selection').hide();
                $('.radio-container').hide();
                 removeAreaSelect();
                // $('#startdatepicker input').val('');
                // $('#enddatepicker input').val('');
                mode = "location";
            }
            if($('.app-selector :selected').val() === "3"){

                $('.single-spatial-selection').show();
                $(".run-service-button-container").show();
                $('.coverage-date-filters').show();
                $('.radio-container').show();
                map.on('click', function(e){
                    if (mode == "location") {
                        $('#lat').val(e.latlng.lat);
                        $('#lon').val(e.latlng.lng);

                        if (user_marker != undefined) {
                            map.removeLayer(user_marker);
                        }

                        user_marker = L.marker([e.latlng.lat, e.latlng.lng], {draggable:true}).bindPopup("AS4254").addTo(map);
                        single_marker_layer = L.layerGroup(user_marker);
                        map.addLayer(single_marker_layer);
                        user_marker.on('dragend', function (e) {
                            // alert(e.target._latlng);
                             $('#lat').val(e.target._latlng.lat);
                             $('#lon').val(e.target._latlng.lng);
                        })
                    }
                    wec_energy_generation_forecast_tour.addSteps([
                        {
                            element: ".radio-container",
                            placement: "left",
                            title: "Wave energy converter selection",
                            content: "Select the converter for your simulation. You can select only one",
                        }
                    ]);
                     wec_energy_generation_forecast_tour.next();
                 });
                wec_energy_generation_forecast_tour.start(true);
                wec_energy_generation_forecast_tour.addSteps([
                    {
                        element: ".single-spatial-selection",
                        placement: "left",
                        title: "Geographic selection",
                        content: "Move the blue area to select the area you wish to execute your service",
                    },

                ]);
                wec_energy_generation_forecast_tour.start(true);
                // wec_energy_generation_forecast_tour.next();
                set_app_dataset_date_pickers("select_dataset_wecs_generation_forecast");
            }
            else{
                // $('#startdatepicker input').val('');
                // $('#enddatepicker input').val('');

                $('#lat').val('');
                $('#lon').val('');

            }
            if($('.app-selector :selected').val() === "4"){
                $('.single-spatial-selection').show();
                $('.dataset-selector').show();
                $(".matching_analysis_dropdown").show();
                $('.coverage-date-filters').show();
                $('.run-service-button-container').show();
                $('.radio-container').show();

                map.on('click', function(e){
                    if (mode == "location") {
                        $('#lat').val(e.latlng.lat);
                        $('#lon').val(e.latlng.lng);

                        $('.dataset-selector').show();

                        $(".item").each(function() {
                            if($(this).hasClass("disabled")) {
                                $(this).removeClass("disabled");
                            }
                        });

                        $('#matching_analysis_dropdown  option').each(function () {
                            if($(this).data("maxlat") < e.latlng.lat || $(this).data("minlat") > e.latlng.lat || $(this).data("minlng") > e.latlng.lng || $(this).data("maxlng") < e.latlng.lng){
                                var dropdown_id = $(this).val();
                                $(`.item[data-value="${dropdown_id}"]`).addClass("disabled");
                            }
                        });

                        if (user_marker != undefined) {
                            map.removeLayer(user_marker);
                        }

                        user_marker = L.marker([e.latlng.lat, e.latlng.lng], {draggable:true}).bindPopup("AS4254").addTo(map);
                        single_marker_layer = L.layerGroup(user_marker);
                        map.addLayer(single_marker_layer);
                        user_marker.on('dragend', function (e) {
                            // alert(e.target._latlng);
                             $('#lat').val(e.target._latlng.lat);
                             $('#lon').val(e.target._latlng.lng);
                        })

                        if(matching_analysis_tour.getCurrentStep()	 == 0){
                            matching_analysis_tour.addStep({
                                element: ".dataset-selector",
                                placement: "left",
                                title: "Dataset selection",
                                content: "Dataset selection for application's execution",
                            });
                            matching_analysis_tour.next();
                        }
                    }
                });
                 matching_analysis_tour.addStep(
                {
                    element: ".single-spatial-selection",
                    placement: "left",
                    title: "Geographic selection",
                    content: "Click on the map to place your marker or manually set your coordinates",
                });
                matching_analysis_tour.start(true);
                matching_analysis_tour.next();
                set_app_dataset_date_pickers("select_dataset_matching_analysis");
            }
            else{
                $('#lat').val('');
                $('#lon').val('');
                $(".matching_analysis_dropdown").hide();
            }
        })
    });







    function get_app_url() {

        if($('.app-selector :selected').val() === "1"){
            var url = "/wave-energy/energy_conversion/evaluate_location/";
            return url;
        }
        else if($('.app-selector :selected').val() === "2"){
            var url = "/wave-energy/energy_conversion/evaluate_area/";
            return url;
        }
        else if($('.app-selector :selected').val() === "3") {
            var url = "/wave-energy/energy_conversion/generation_forecast/";
            return url;
        }
        else if($('.app-selector :selected').val() === "4"){

            var url = "/wave-energy/energy_conversion/evaluate_area/";
            return url;
        }
   }

    function get_parameters(){

        var lat = $("#lat").val();
        var lng = $("#lon").val();

        var data_radius = $("#data-radius").data('value');

        var lat_to = parseFloat(lat) + parseFloat(data_radius);
        var lng_to = parseFloat(lng) + parseFloat(data_radius);
        var lat_from = parseFloat(lat) -  parseFloat(data_radius);
        var lng_from = parseFloat(lng) -  parseFloat(data_radius);

        var start_date = $( "#startdatepicker input" ).datepicker({ dateFormat: "yy-mm-dd" }).val();
        var enddate = $( "#enddatepicker input" ).datepicker({ dateFormat: "yy-mm-dd" }).val();


        if($('.app-selector :selected').val() === "1"){

            var dataset_id = $("#select_dataset_wecs_assessment_location :selected").val();
            var selected_converters = [];
            $("#converters-selector :selected").each(function () {
                selected_converters.push($(this).val());
            });
            var converters_str = "";
            for(var i = 0; i < selected_converters.length; i++){
                converters_str +="&converters[]="+selected_converters[i];
            }

            var url = "?dataset_id="+dataset_id+"&start_date="+start_date+
                "&end_date="+enddate+"&latitude_from="+lat_from+"&latitude_to="+lat_to+
                "&longitude_from="+lng_from+"&longitude_to="+lng_to+""+converters_str;
            return url;
        }
        else if($('.app-selector :selected').val() === "3"){
            var selected_converter = $('input[name=wec]:checked').val();
            var url = "?start_date="+start_date+
                "&end_date="+enddate+"&latitude_from="+lat_from+"&latitude_to="+lat_to+
                "&longitude_from="+lng_from+"&longitude_to="+lng_to+"&converters[]="+selected_converter;
            return url;
        }
        else if($('.app-selector :selected').val() === "4"){

            var dataset_id = $("#select_dataset_data_visualisation :selected").val();

            var selected_variables = [];
            $("#"+dataset_id+"-variables :selected").each(function () {
                selected_variables.push($(this).val());
            });
            var variables_str = "";
            for(var i = 0; i < selected_variables.length; i++){
                variables_str +="&variables[]="+selected_variables[i];
            }


            var url = "?dataset_id="+dataset_id+"&start_date="+start_date+
                "&end_date="+enddate+"&latitude_from="+lat_from+"&latitude_to="+lat_to+"&longitude_from="+lng_from+
                "&longitude_to="+lng_to+""+variables_str;
            return url;
       }
        else if($('.app-selector :selected').val() === "2"){

            var lat_from = $("#lat_min").val();
            var lat_to = $("#lat_max").val();
            var lng_from = $("#lon_min").val();
            var lng_to = $("#lon_max").val();

            var dataset_id = $("#select_dataset_wave_resource_assessment_area :selected").val();

            var selected_converter = $('input[name=wec]:checked').val();

            var url = "?dataset_id="+dataset_id+"&start_date="+start_date+
                "&end_date="+enddate+"&latitude_from="+lat_from+"&latitude_to="+lat_to+
                "&longitude_from="+lng_from+"&longitude_to="+lng_to+"&converters[]="+selected_converter;
           return url;
        }

   }

    var exec_instance = '';
    var execution_status_interval;

    function execution_status_stop() {
      clearInterval(execution_status_interval);
    }
    $("#run-service-btn").click(function () {
       // var execution_url = create_execution_url();
       var app_url = get_app_url();
       // alert(app_url);
       var parameters = get_parameters();
       if (app_url === "/wave-energy/energy_conversion/evaluate_location/"){
           $("#execution_btn_WEC_LOCATION_EVALUATION_SERVICE").click();
       }
       if (app_url === "/wave-energy/energy_conversion/generation_forecast/"){
           $("#execution_btn_WEC_GENERATION_FORECAST_SERVICE").click();
       }
       if (app_url === "/wave-energy/energy_conversion/evaluate_area/"){
           $("#execution_btn_WEC_AREA_EVALUATION_SERVICE").click();
       }
       if (app_url === "/wave-energy/energy_conversion/data_visualisation/") {
            $("#execution_btn_WEC_DATA_VISUALISATION_SERVICE").click();
       }

       $("#execution_status").val('starting service');

       if (app_url === "/wave-energy/data_visualisation/") {
            $(location).attr("href", app_url+"execute/"+parameters);
       }
       else{
           console.log(app_url+"execute/"+parameters);
            $.ajax({
            "type": "GET",
            "url": app_url+"execute/"+parameters,
            "data": {},
            "success": function(result) {
                    console.log(result);
                    exec_instance = result['exec_instance'];
                },
                error: function () {
                    alert('error');
                }
            });

            execution_status_interval = setInterval(check_execution_status, 3000);

            function check_execution_status() {
                $.ajax({
                    "type": "GET",
                    "url": app_url+"status/"+exec_instance+"/",
                    "data": {},
                    "success": function(result) {
                        console.log(result["status"]);
                        $("#execution_status").val(result["status"]);
                        if(result["status"] === "done"){
                            setTimeout(function() {
                                execution_status_stop();
                                window.location.href = app_url+"results/"+exec_instance+"/";
                            }, 1000);
                        }
                        else if (result["status"] === "failed") {
                            execution_status_stop();
                            // alert("execution failed");
                        }
                    },
                    error: function () {
                        execution_status_stop();
                        // alert('error');
                    }
                });
            }

       }

   });


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
                $(".modal.in .progress-bar").css({width: '100%', background: '#db2828'});
                $(".modal.in .status_counter").each(function (index, elem) {
                    $(elem).removeClass('label-default').addClass('label-primary');
                });
                $(".modal.in #modal_dismiss_btn_cancel").hide();
                $(".modal.in #modal_dismiss_btn_close").show();
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


    $('body').on('click', '#modal_dismiss_btn_cancel', function () {
        console.log("hit cancel");
        $("#execution_status").val("failed");
        $(" .modal.in #modal_status_input").val("cancelling");
        $.ajax({
            "type": "GET",
            "url": "/wave-energy/cancel_execution/"+exec_instance+"/",
            "data": {},
            "success": function(result) {
                console.log('service cancelled');
            },
            error: function () {
                console.log('error cancelling service');
            },
        });
    });

    $("#add-wec-btn").click();
});