
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

    tour.init();

    tour.start(true);

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
    wecs_location_assessment_tour.init();

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
    wec_assessment_area_tour.init();

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
    wec_energy_generation_forecast_tour.init();

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
    matching_analysis_tour.init();

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
       })
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
                (function (window, document, undefined) {
                        "use strict";

                        var wrap = document.getElementById("wrap"),
                            setColumn = document.getElementById("column"),
                            setRow = document.getElementById("row"),
                            btnGen = document.getElementById("btnGen"),
                            btnCopy = document.getElementById("btnCopy");

                        btnGen.addEventListener("click", generateTable);
                        btnCopy.addEventListener("click", copyTo);

                        function generateTable(e) {
                            var newTable = document.createElement("table"),
                                tBody = newTable.createTBody(),
                                nOfColumns = parseInt(setColumn.value, 10),
                                nOfRows = parseInt(setRow.value, 10),
                                row = generateRow(nOfColumns);

                            newTable.createCaption().appendChild(document.createTextNode("Generated Table"));

                            for (var i = 0; i < nOfRows; i++) {
                                tBody.appendChild(row.cloneNode(true));
                            }

                            (wrap.hasChildNodes() ? wrap.replaceChild : wrap.appendChild).call(wrap, newTable, wrap.children[0]);
                        }

                        function generateRow(n) {
                            var row = document.createElement("tr"),
                                text = document.createElement("input");
                                text.setAttribute("type", "text");
                                text.setAttribute("value", "0");

                            for (var i = 0; i < n; i++) {
                                row.insertCell().appendChild(text.cloneNode(true));
                            }

                            return row.cloneNode(true);
                        }

                        function copyTo(e) {
                            prompt("Copy to clipboard: Ctrl+C, Enter", wrap.innerHTML);
                        }
                    }(window, window.document));
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

                    //  $(".item").each(function() {
                    //     if($(this).hasClass("disabled")) {
                    //         $(this).removeClass("disabled");
                    //     }
                    // });

                        //  $('#select_dataset_wave_resource_assessment_area  option').each(function () {
                        //     if($(this).data("maxlat") < bounds[2] || $(this).data("minlat") >bounds[0] || $(this).data("minlng") > bounds[1] || $(this).data("maxlng") < bounds[3]){
                        //         var dropdown_id = $(this).val();
                        //         $(`.item[data-value="${dropdown_id}"]`).addClass("disabled");
                        //     }
                        // });
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

                    // $(".item").each(function() {
                    //     if($(this).hasClass("disabled")) {
                    //         $(this).removeClass("disabled");
                    //     }
                    // });

                        //  $('#select_dataset_wave_resource_assessment_area  option').each(function () {
                        //     if($(this).data("maxlat") < bounds[2] || $(this).data("minlat") >bounds[0] || $(this).data("minlng") > bounds[1] || $(this).data("maxlng") < bounds[3]){
                        //         var dropdown_id = $(this).val();
                        //         $(`.item[data-value="${dropdown_id}"]`).addClass("disabled");
                        //     }
                        // });
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
    })

    $("#save_converter").click(function () {
        $.ajax({
            "type": "GET",
            "url": 'energy-conversion/new_wec/',
            "wec_data":
        })
    })
});