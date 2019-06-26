
var buoys_layer;
var single_marker_layer;
var user_marker = {};
var buoys_markers = [];
var mode=null;
var dataset_id;
var buoys_dict;

$(document).ready(function() {
    var wave_forecast_tour;
    function init_wave_forecast_tour() {
        wave_forecast_tour = new Tour({
            storage: false,
            template: "<div class='popover tour' style='min-width: 350px; min-height: 120px; color: black;'>" +
            "<div class='arrow'></div>" +
            "<h3 class='popover-title' style='box-shadow: 0px 1px #bfbfbf;'></h3>" +
            "<div class='popover-content'></div>" +
            // "<div class='popover-navigation'>" +
            // "<button class='btn btn-sm btn-primary' data-role='prev'>« Prev</button>" +
            // "<span data-role='separator'>|</span>" +
            // "<button class='btn btn-sm btn-primary' data-role='next'>Next »</button>" +
            "<button class='btn btn-sm btn-primary pull-right' data-role='end'>End tour</button>" +
            // "</div>" +
            "</div>"
        });
        wave_forecast_tour.addStep({
            element: ".single-spatial-selection",
            placement: "left",
            title: "Geographic selection",
            content: "Click on the map to place your marker or manually set your coordinates"
        });
        wave_forecast_tour.addStep({
            element: ".dataset-selector",
            placement: "left",
            title: "Dataset selection",
            content: "Dataset selection for application's execution"
        });

        wave_forecast_tour.addStep({
            element: "#run-service-btn",
            placement: "left",
            title: "Service Execution",
            content: "Ready to execute!"
        });
        wave_forecast_tour.init();
        wave_forecast_tour.start(true);
    }

    var data_visualization_tour;
    function init_data_visualization_tour(){
        data_visualization_tour = new Tour({
            storage: false,
            template: "<div class='popover tour' style='min-width: 350px; min-height: 120px; color: black;'>" +
                "<div class='arrow'></div>" +
                "<h3 class='popover-title' style='box-shadow: 0px 1px #bfbfbf;'></h3>" +
                "<div class='popover-content'></div>" +
                "<div class='popover-navigation'>" +
                // "<button class='btn btn-sm btn-primary' data-role='prev'>« Prev</button>" +
                // "<span data-role='separator'>|</span>" +
                // "<button class='btn btn-sm btn-primary' data-role='next'>Next »</button>" +
                "<button class='btn btn-sm btn-primary pull-right' data-role='end'>End tour</button>" +
                "</div>" +
                "</div>",
        });
        data_visualization_tour.addStep({
            element: ".single-spatial-selection",
            placement: "left",
            title: "Geographic selection",
            content: "Click on the map to place your marker or manually set your coordinates"
        });
        data_visualization_tour.addStep({
            element: ".dataset-selector",
            placement: "left",
            title: "Dataset selection",
            content: "Dataset selection for application's execution"
        });

        data_visualization_tour.addStep({
            element: ".variable-selector",
            placement: "left",
            title: "Variable selection",
            content: "Select at least one the available variables of the selected dataset"
        });
        data_visualization_tour.addSteps([{
            element: ".coverage-date-filters",
            placement: "left",
            title: "Service timeframe",
            duration: 5000,
            content: "Select the timeframe you wish to run the service. By default, minimum and maximum values of the dataset are selected",
        },{
            element: "#run-service-btn",
            placement: "left",
            title: "Service Execution",
            content: "Ready to execute!"

        }]);
        data_visualization_tour.init();
        data_visualization_tour.start(true);
    }

    var wave_resource_assesment_single_tour;
    function init_wave_resource_assesment_single_tour(){
        wave_resource_assesment_single_tour = new Tour({
            storage: false,
            template: "<div class='popover tour' style='min-width: 350px; min-height: 120px; color: black;'>" +
                "<div class='arrow'></div>" +
                "<h3 class='popover-title' style='box-shadow: 0px 1px #bfbfbf;'></h3>" +
                "<div class='popover-content'></div>" +
                "<div class='popover-navigation'>" +
                // "<button class='btn btn-sm btn-primary' data-role='prev'>« Prev</button>" +
                // "<span data-role='separator'>|</span>" +
                // "<button class='btn btn-sm btn-primary' data-role='next'>Next »</button>" +
                "<button class='btn btn-sm btn-primary pull-right' data-role='end'>End tour</button>" +
                "</div>" +
                "</div>"
        });
        wave_resource_assesment_single_tour.addStep({
            element: ".single-spatial-selection",
            placement: "left",
            title: "Geographic selection",
            content: "Click on the map to place your marker or manually set your coordinates"
        });
        wave_resource_assesment_single_tour.addStep({
            element: ".dataset-selector",
            placement: "left",
            title: "Dataset selection",
            content: "Dataset selection for application's execution"
        });
        wave_resource_assesment_single_tour.addSteps([{
            element: ".coverage-date-filters",
            placement: "left",
            title: "Service timeframe",
            duration: 3500,
            content: "Select the timeframe you wish to run the service. By default, minimum and maximum values of the dataset are selected"
        },{
            element: "#run-service-btn",
            placement: "left",
            title: "Service Execution",
            content: "Ready to execute!"
        }]);
        wave_resource_assesment_single_tour.init();
        wave_resource_assesment_single_tour.start(true);
    }

    var wave_resource_area_tour;
    function init_wave_resource_area_tour() {
        wave_resource_area_tour = new Tour({
            storage: false,
            template: "<div class='popover tour' style='min-width: 350px; min-height: 120px; color: black;'>" +
            "<div class='arrow'></div>" +
            "<h3 class='popover-title' style='box-shadow: 0px 1px #bfbfbf;'></h3>" +
            "<div class='popover-content'></div>" +
            "<div class='popover-navigation'>" +
            // "<button class='btn btn-sm btn-primary' data-role='prev'>« Prev</button>" +
            // "<span data-role='separator'>|</span>" +
            // "<button class='btn btn-sm btn-primary' data-role='next'>Next »</button>" +
            "<button class='btn btn-sm btn-primary pull-right' data-role='end'>End tour</button>" +
            "</div>" +
            "</div>"
        });
        wave_resource_area_tour.addSteps([{
            element: ".spatial-selection",
            placement: "left",
            title: "Geographic selection",
            duration: 3000,
            content: "Move the area select to the area you wish to execute your service"
        },{
            element: ".dataset-selector",
            placement: "left",
            title: "Dataset selection",
            content: "Dataset selection for application's execution"
        }]);

        wave_resource_area_tour.addSteps([{
            element: ".coverage-date-filters",
            placement: "left",
            title: "Service timeframe",
            duration: 3500,
            content: "Select the timeframe you wish to run the service. By default, minimum and maximum values of the dataset are selected"
        },{
            element: "#run-service-btn",
            placement: "left",
            title: "Service Execution",
            content: "Ready to execute!"

        }]);
        wave_resource_area_tour.init();
        wave_resource_area_tour.start(true);
    }

    var tour = new Tour({
        storage: false,
        template: "<div class='popover tour' style='min-width: 350px; min-height: 120px; color: black;'>" +
            "<div class='arrow'></div>" +
            "<h3 class='popover-title' style='box-shadow: 0px 1px #bfbfbf;'></h3>" +
            "<div class='popover-content'></div>" +
            "<div class='popover-navigation'>" +
            // "<button class='btn btn-sm btn-primary' data-role='prev'>« Prev</button>" +
            // "<span data-role='separator'>|</span>" +
            // "<button class='btn btn-sm btn-primary' data-role='next'>Next »</button>" +
            // "<button class='btn btn-sm btn-primary pull-right' data-role='end'>End tour</button>" +
            "</div>" +
            "</div>"
    });
    tour.addStep({
        element: ".app-selector",
        placement: "left",
        title: "Application selection",
        content: "Please select the application for use"
    });
    tour.init();
    tour.start(true);


    function create_buoys_dataset_dict() {
        var buoys_dict = [];
        $('.buoy').each(function(i, obj) {

            var my_list = [];
            var buoy_id = $(this).data("id");
            var dataset_id = $(this).data("dataset_id");
            my_list.push(buoy_id, dataset_id);
            buoys_dict.push(my_list);
        });
        return buoys_dict;
    }

    buoys_dict = create_buoys_dataset_dict();

    function create_buoys_plane(){
        var buoys_plane = [];
        $('.buoy').each(function(i, obj) {
            var buoy_id = $(this).data("id");
            var buoy_lat = $(this).data("lat");
            var buoy_lon = $(this).data("lon");
            var buoy = [buoy_id, buoy_lat, buoy_lon];

            //check if the buoy is for the data visualization application
            for (var i = 0; i < buoys_dict.length; i++){
                if(buoys_dict[i][0] == buoy_id){
                     $('#select_dataset_data_visualisation  option').each(function () {
                         if (buoys_dict[i][1] == $(this).val())
                             buoys_plane.push(buoy);
                     });
                }

            }
        });


        var redIcon = new L.Icon({
          iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'
        });
        for (var i = 0; i < buoys_plane.length; i++){
            marker = new L.marker([buoys_plane[i][1],buoys_plane[i][2]], {icon: redIcon}).bindPopup(buoys_plane[i][0]).on('click', erase_user_marker);
            buoys_markers.push(marker);
        }
        buoys_layer = L.layerGroup(buoys_markers);

        map.addLayer(buoys_layer);
    }

    function removeAreaSelect() {
        var layers_arr = Object.values(map._layers);
        layers_arr.shift();
        $.each(layers_arr, function(i, e){e.remove()});
    }

    function set_forecast_timeframe(dataset_selected) {
        if(dataset_selected){
            var startDate = new Date();
            startDate.setDate(startDate.getDate() + 1);
            startDate.setHours(0, 0, 0, 0);
            var startpick = $('#startdatepicker').datetimepicker({
                autoclose: true,
                pickerPosition: 'top-left',
                startDate: startDate,
                endDate: startDate,
            });
            $('#startdatepicker').datetimepicker("update", startDate);
            $('#startdatepicker').datetimepicker('setStartDate', startDate);
            $('#startdatepicker').datetimepicker('setEndDate', startDate);

            var endDate = new Date();
            endDate.setDate(endDate.getDate() + 7);
            endDate.setHours(23, 59, 59, 999);
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
        else{
            $('#startdatepicker').find("input[type=text], textarea").val("").val('');
            $('#enddatepicker').find("input[type=text], textarea").val("").val('');
        }
    }


    $('#select_app').val('').trigger("change").dropdown('clear');
    $('#select_dataset').dropdown('clear');
    $('.ui.dropdown').dropdown('clear');


    var dataset_selection = $('#select_dataset_data_visualisation :selected').val();

    $('#'+dataset_selection+'-variables').show();

    function create_new_area_select(area_select_bounds){
        $(".leaflet-interactive").remove();
        var areaSelect = L.rectangle(area_select_bounds);
        map.addLayer(areaSelect);
        areaSelect.editing.enable();
        area_bounds = areaSelect.getBounds();
        areaSelect.on("edit", function() {
            area_bounds = this.getBounds();
            $('#lat_min').val((area_bounds._southWest.lat).toFixed(4));
            $('#lat_max').val((area_bounds._northEast.lat).toFixed(4));
            $('#lon_min').val((area_bounds._southWest.lng).toFixed(4));
            $('#lon_max').val((area_bounds._northEast.lng).toFixed(4));
            update_dataset_list_area();
            if(wave_resource_area_tour.getCurrentStep() !== 1)
                wave_resource_area_tour.goTo(1);
        });
        // map.fitBounds(area_select_bounds);
        bounds = [area_select_bounds[0][0],area_select_bounds[0][1],area_select_bounds[1][0],area_select_bounds[1][1]];
        $('#lat_min').val(bounds[0]);
        $('#lat_max').val(bounds[2]);
        $('#lon_min').val(bounds[1]);
        $('#lon_max').val(bounds[3]);
    }

    function erase_user_marker(){

        var redIcon = new L.Icon({
          iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'
        });
        for(var i = 0; i < buoys_markers.length; i++){
            buoys_markers[i].setIcon(redIcon);
        }
        $(".item").each(function() {
            if($(this).hasClass("disabled")){
                $(this).removeClass("disabled");
            }
        });
        var selected_buoy = this.getPopup().getContent();

        for(var i = 0; i < buoys_dict.length; i++){
            if(buoys_dict[i][0] === selected_buoy){
                dataset_id = buoys_dict[i][1];
                break;
            }
        }
        $('.dataset-selector').show();
        $('.variable-selector').show();

        //select the dataset which the buoy belongs
        $("#select_dataset_data_visualisation").val(dataset_id);
        $("#select_dataset_data_visualisation").change();
        $("#select_dataset_data_visualisation option").each(function() {

            if ($(this).val() != dataset_id && $(this).val() !== ""){
                var dropdown_id = $(this).val();

                $(`.item[data-value="${dropdown_id}"]`).addClass("disabled");
            }

        });


         var dataset_selection = $('#select_dataset_data_visualisation :selected').val();

        $('#'+dataset_selection+'-variables').show();
        var newIcon = new L.Icon({iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png'});
        this.setIcon(newIcon);

        $('#lat').val(this.getLatLng().lat);
        $('#lon').val(this.getLatLng().lng).trigger("change");

        if(user_marker != undefined){
            map.removeLayer(user_marker);
        }
    }

    function reset_dropdowns(){
        console.log("lat/lon change");
        $(".item").removeClass("disabled");
        $('.dataset-selector select option').attr('selected', false);

        $('#select_dataset_wave_forecast').dropdown('clear');
        $('#select_dataset_wave_resource_assessment_area').dropdown('clear');
        $('#select_dataset_data_visualisation').dropdown('clear');
        $('#select_dataset_wave_resource_assessment_single').dropdown('clear');
    }

    function update_dataset_list_location(){
        reset_dropdowns();
        $('.dataset-selector select option').each(function (idx, elem) {
            if( parseFloat($(elem).data("maxlat")) < parseFloat($('#lat').val()) ||
                parseFloat($(elem).data("minlat")) > parseFloat($('#lat').val()) ||
                parseFloat($(elem).data("minlng")) > parseFloat($('#lon').val()) ||
                parseFloat($(elem).data("maxlng")) < parseFloat($('#lon').val())
            ){
                var dropdown_id = $(elem).val();
                $('.item[data-value="'+dropdown_id+'"]').addClass("disabled");
            }
        });
    }

    function update_dataset_list_area(){
        reset_dropdowns();
        $('.dataset-selector select option').each(function (idx, elem) {
            if( parseFloat($(elem).data("maxlat")) < parseFloat($('#lat_min').val()) ||
                parseFloat($(elem).data("minlat")) > parseFloat($('#lat_max').val()) ||
                parseFloat($(elem).data("minlng")) > parseFloat($('#lon_max').val()) ||
                parseFloat($(elem).data("maxlng")) < parseFloat($('#lon_min').val())
            ){
                var dropdown_id = $(elem).val();
                $('.item[data-value="'+dropdown_id+'"]').addClass("disabled");
            }
        });
    }

    $(function () {
        function interractive_marker(onLocationfound, user_marker) {
            function check_marker_position(lat, lon, user_marker, lat_selector, lon_selector){
                lat_selector.val(lat.toFixed(4));
                lon_selector.val(lon.toFixed(4));
            }

            $('#lat').on('input',function () {
                if($('#lat').val()<-90){
                    $('#lat').val((-90).toFixed(4));
                }else if($('#lat').val()>90){
                    $('#lat').val((90).toFixed(4));
                }
                onLocationfound({latlng:[$('#lat').val(),$('#lon').val()]});
            });
            $('#lat').on('change',function () {
                if (($('#lat').val() !== '') && ($('#lat').val() !== undefined) && ($('#lat').val()!== null)) {
                    check_marker_position(parseFloat($('#lat').val()),parseFloat($('#lon').val()),user_marker, $('#lat'),$('#lon'))
                }
            });
            $('#lon').on('input',function () {
                if($('#lon').val()<-180){
                    $('#lon').val((-180).toFixed(4));
                }else if($('#lon').val()>180){
                    $('#lon').val((180).toFixed(4));
                }
                onLocationfound({latlng:[$('#lat').val(),$('#lon').val()]});
            });
            $('#lon').on('change',function () {
                if (($('#lon').val() !== '') && ($('#lon').val() !== undefined) && ($('#lon').val()!== null)) {
                    check_marker_position(parseFloat($('#lat').val()),parseFloat($('#lon').val()),user_marker,$('#lat'),$('#lon'))
                }
            });

        };
        $('#lat, #lon').change(function () {
            update_dataset_list_location();
        });

        $('.app-selector').change(function () {
            $('#lat').val('');
            $('#lon').val('');
            $('#lat_min').val('');
            $('#lat_max').val('');
            $('#lon_min').val('');
            $('#lon_max').val('');
            //Wave Forecast Scenario
            if ($('.app-selector :selected').val() == "Wave_Forecast") {
                $('.wave_resource_assessment_area_dropdown').hide();
                $('.wave_resource_assessment_single_dropdown').hide();
                $('.data_visualisation_dropdown').hide();
                $('.variable-selector').hide();
                $('.coverage-date-filters').show();
                $('#wave-forecast-results').show();
                $('.single-spatial-selection').show();
                $(".run-service-button-container").show();
                $(".wave_forecast_dropdown").show();

                init_wave_forecast_tour();
                wave_forecast_tour.goTo(0);

                map.off('click');
                map.on('click', function(e){
                    if (mode == "location") {
                        $('#lat').val(e.latlng.lat);
                        $('#lon').val(e.latlng.lng).trigger("change");

                        $('.dataset-selector').show();
                        $("#select_dataset_wave_forecast").off('change');
                        $("#select_dataset_wave_forecast").change(function () {
                            if(parseInt($(this).val()) > 0){
                                wave_forecast_tour.goTo(2);
                                /* Set Up Time Pickers For Start/End Date  */
                                set_forecast_timeframe(true);
                            }
                            else{
                                set_forecast_timeframe(false);
                            }
                        });

                        if (user_marker != undefined) {
                            map.removeLayer(user_marker);
                        }
                        user_marker = L.marker([e.latlng.lat, e.latlng.lng], {draggable:true}).bindPopup("AS4254").addTo(map);
                        single_marker_layer = L.layerGroup(user_marker);
                        onLocationfound = function(e){
                            user_marker.setLatLng(e.latlng).update();
                        };
                        user_marker.on('dragend', function (e) {
                            $('#lat').val(e.target._latlng.lat);
                            $('#lon').val(e.target._latlng.lng).trigger("change");
                            wave_forecast_tour.goTo(1);
                        });
                        map.addLayer(single_marker_layer);
                        map.on('locationfound', onLocationfound);
                        interractive_marker(onLocationfound, user_marker);

                    }

                    wave_forecast_tour.goTo(1);
                });


            }
            else{
                $('.single-spatial-selection').hide();
                $('.dataset-selector').hide();
                $('.coverage-date-filters').show();
                $('#wave-forecast-results').hide();
                $('#startdatepicker input').val('');
                $('#enddatepicker input').val('');
                $(".wave_forecast_dropdown").hide();
                // $('#enddatepicker').datepicker('remove');
                // $('#startdatepicker').datepicker('remove');
                startdate = null;
                enddate = null;

            }
            if ($('.app-selector :selected').val() == "Wave_Resource_Assessment_area"){
                $('.wave_resource_assessment_single_dropdown').hide();
                $('.data_visualisation_dropdown').hide();
                $(".wave_forecast_dropdown").hide();
                mode = "area";
                $("#map").css("cursor", "grab");
                $('.dataset-selector').show();
                $('.wave_resource_assessment_area_dropdown').show();
                $('.spatial-selection').show();
                $('#wave-atlas-results').show();
                $(".run-service-button-container").show();

                create_new_area_select([[35,-16],[45,5]]);
                init_wave_resource_area_tour();
                wave_resource_area_tour.goTo(0);

                $('.dataset-selector').show();
                $("#select_dataset_wave_resource_assessment_area").off('change');
                $("#select_dataset_wave_resource_assessment_area").change(function () {
                    set_app_dataset_date_pickers("select_dataset_wave_resource_assessment_area");
                    if(parseInt($(this).val()) > 0){
                        wave_resource_area_tour.goTo(2);
                    }
                });

                // map.mouseup(function() {
                //     area_bounds = areaSelect.getBounds();
                //     var swlat = Math.round(area_bounds.getSouthWest().lat * 10000) / 10000;
                //     var swlon = Math.round(area_bounds.getSouthWest().lng * 10000) / 10000;
                //     var nelat = Math.round(area_bounds.getNorthEast().lat * 10000) / 10000;
                //     var nelon = Math.round(area_bounds.getNorthEast().lng * 10000) / 10000;
                //     bounds = [swlat, swlon, nelat, nelon];
                //     $('#lat_min').val(bounds[0]);
                //     $('#lat_max').val(bounds[2]);
                //     $('#lon_min').val(bounds[1]);
                //     $('#lon_max').val(bounds[3]).trigger("change");
                // });
                //
                // $('.leaflet-edit-resize').mouseup(function(){
                //     area_bounds = areaSelect.getBounds();
                //     var swlat = Math.round(area_bounds.getSouthWest().lat * 10000) / 10000;
                //     var swlon = Math.round(area_bounds.getSouthWest().lng * 10000) / 10000;
                //     var nelat = Math.round(area_bounds.getNorthEast().lat * 10000) / 10000;
                //     var nelon = Math.round(area_bounds.getNorthEast().lng * 10000) / 10000;
                //     bounds = [swlat,swlon,nelat,nelon];
                //     $('#lat_min').val(bounds[0]);
                //     $('#lat_max').val(bounds[2]);
                //     $('#lon_min').val(bounds[1]);
                //     $('#lon_max').val(bounds[3]).trigger("change");
                // });

                // $('#lat_min, #lat_max, #lon_min, #lon_max').change(function () {
                //     bounds = [parseFloat($('#lat_min').val()),parseFloat($('#lon_min').val()),parseFloat($('#lat_max').val()),parseFloat($('#lon_max').val())];
                //     $(".leaflet-interactive").remove();
                //     create_new_area_select([[parseFloat($('#lat_min').val()),parseFloat($('#lon_min').val())],[parseFloat($('#lat_max').val()),parseFloat($('#lon_max').val())]]);
                //     wave_resource_area_tour.goTo(1);
                // });
            }
            else {
                mode = "location";
                $("#map").css("cursor", "pointer");
                $('.wave_resource_assessment_area_dropdown').hide();
                $('#wave-atlas-results').hide();
                $('.spatial-selection').hide();
                removeAreaSelect();

            }
            if ($('.app-selector :selected').val() == "Data_Visualisation"){
                $('.wave_resource_assessment_area_dropdown').hide();
                $('.wave_resource_assessment_single_dropdown').hide();
                $(".wave_forecast_dropdown").hide();
                $('.data_visualisation_dropdown').show();
                $('.single-spatial-selection').show();
                $('#data-visualisation-results').show();
                $(".run-service-button-container").show();

                init_data_visualization_tour();
                data_visualization_tour.goTo(0);

                create_buoys_plane();
                map.off('click');
                map.on('click', function(e) {
                    if (mode == "location"){
                        $('#lat').val(e.latlng.lat);
                        $('#lon').val(e.latlng.lng).trigger("change");

                        $('.dataset-selector').show();
                        $("#select_dataset_data_visualisation").off('change');
                        $("#select_dataset_data_visualisation").change(function () {
                            $(".variables-selector").hide();
                            set_app_dataset_date_pickers("select_dataset_data_visualisation");
                            if(parseInt($(this).val()) > 0){
                                var dataset_id = $(this).val();
                                $('#'+dataset_id+'-variables').show();
                                data_visualization_tour.goTo(2);
                            }
                        });
                        $(".variables-selector").change(function () {
                            if($(this).find("select").val().length > 0){
                                data_visualization_tour.goTo(3);
                            }
                        });
                        $('.variable-selector').show();

                        //make again the buoys layer red
                        var redIcon = new L.Icon({iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'});
                        for(var i = 0; i < buoys_markers.length; i++)
                            buoys_markers[i].setIcon(redIcon);

                        if (user_marker != undefined) {
                            map.removeLayer(user_marker);
                        }
                        user_marker = L.marker([e.latlng.lat, e.latlng.lng], {draggable:true}).bindPopup("AS4254").addTo(map);
                        single_marker_layer = L.layerGroup(user_marker);
                        onLocationfound = function(e){
                            user_marker.setLatLng(e.latlng).update();
                        };
                        user_marker.on('dragend', function (e) {
                            $('#lat').val(e.target._latlng.lat);
                            $('#lon').val(e.target._latlng.lng).trigger("change");
                            data_visualization_tour.goTo(1);
                        });
                        map.addLayer(single_marker_layer);
                        map.on('locationfound', onLocationfound);
                        interractive_marker(onLocationfound, user_marker);
                        data_visualization_tour.goTo(1);
                    }
                 });
            }
            else{
                $('.data_visualisation_dropdown').hide();
                $('#data-visualisation-results').hide();
                $('.variable-selector').hide();
                $('.data_visualisation_dropdown').hide();
                // $('.single-spatial-selection').hide();

                if(map.hasLayer(buoys_layer)) {
                    map.removeLayer(buoys_layer);
                }
            }
            if ($('.app-selector :selected').val() == "Wave_Resource_Assessment_single"){
                $('.wave_resource_assessment_area_dropdown').hide();

                $('.data_visualisation_dropdown').hide();
                $(".wave_forecast_dropdown").hide();

                $('.wave_resource_assessment_single_dropdown').show();
                $('#wave-resource-assessment').show();
                $('.single-spatial-selection').show();
                $(".run-service-button-container").show();

                init_wave_resource_assesment_single_tour();
                wave_resource_assesment_single_tour.goTo(0);

                map.off('click');
                map.on('click', function(e){
                    if (mode == "location") {
                        $('#lat').val(e.latlng.lat);
                        $('#lon').val(e.latlng.lng).trigger("change");

                        $('.dataset-selector').show();
                        $("#select_dataset_wave_resource_assessment_single").off('change');
                        $("#select_dataset_wave_resource_assessment_single").change(function () {
                            set_app_dataset_date_pickers("select_dataset_wave_resource_assessment_single");
                            if(parseInt($(this).val()) > 0){
                                wave_resource_assesment_single_tour.goTo(2);
                            }
                        });

                        if (user_marker != undefined) {
                            map.removeLayer(user_marker);
                        }

                        user_marker = L.marker([e.latlng.lat, e.latlng.lng], {draggable:true}).bindPopup("AS4254").addTo(map);
                        single_marker_layer = L.layerGroup(user_marker);
                        onLocationfound = function(e){
                            user_marker.setLatLng(e.latlng).update();
                        };
                        user_marker.on('dragend', function (e) {
                            $('#lat').val(e.target._latlng.lat);
                            $('#lon').val(e.target._latlng.lng).trigger("change");
                            wave_resource_assesment_single_tour.goTo(1);
                        });
                        map.addLayer(single_marker_layer);
                        map.on('locationfound', onLocationfound);
                        interractive_marker(onLocationfound, user_marker);
                        wave_resource_assesment_single_tour.goTo(1);
                    }
                });
                set_app_dataset_date_pickers("select_dataset_wave_resource_assessment_single");
            }
            else {
                    $('.wave_resource_assessment_single_dropdown').hide();
                    $('#wave-resource-assessment').hide();
             }
        })
    });



    function set_app_dataset_date_pickers(app_selector) {
       // $('#'+app_selector).change(function () {
            var dataset_id = $('#'+app_selector+" :selected").val();
            console.log("in set_app_dataset_date_pickers");
            console.log(app_selector);
            console.log(dataset_id);
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
       // })
   }

    function get_app_url() {

        if($('.app-selector :selected').val() === "Wave_Resource_Assessment_single"){
            var url = "/wave-energy/evaluate_location/";
            return url;
        }
        else if($('.app-selector :selected').val() === "Wave_Forecast"){
            var url = "/wave-energy/wave_forecast/";
            return url;
        }
        else if($('.app-selector :selected').val() === "Data_Visualisation"){
            var url = "/wave-energy/data_visualisation/";
            return url;
        }
        else if($('.app-selector :selected').val() === "Wave_Resource_Assessment_area"){

            var url = "/wave-energy/evaluate_area/";
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


        if($('.app-selector :selected').val() === "Wave_Resource_Assessment_single"){

            var dataset_id = $("#select_dataset_wave_resource_assessment_single :selected").val();

            var url = "?dataset_id="+dataset_id+"&start_date="+start_date+
                "&end_date="+enddate+"&latitude_from="+lat_from+"&latitude_to="+lat_to+
                "&longitude_from="+lng_from+"&longitude_to="+lng_to;
            return url;
        }
        else if($('.app-selector :selected').val() === "Wave_Forecast"){

            var dataset_id = $("#select_dataset_wave_forecast :selected").val();

            var url = "?dataset_id="+dataset_id+"&start_date="+start_date+
                "&end_date="+enddate+"&latitude_from="+lat_from+"&latitude_to="+lat_to+
                "&longitude_from="+lng_from+"&longitude_to="+lng_to;
            return url;
        }
        else if($('.app-selector :selected').val() === "Data_Visualisation"){

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
        else if($('.app-selector :selected').val() === "Wave_Resource_Assessment_area"){

            var lat_from = $("#lat_min").val();
            var lat_to = $("#lat_max").val();
            var lng_from = $("#lon_min").val();
            var lng_to = $("#lon_max").val();

            var dataset_id = $("#select_dataset_wave_resource_assessment_area :selected").val();

            var url = "?dataset_id="+dataset_id+"&start_date="+start_date+
                "&end_date="+enddate+"&latitude_from="+lat_from+"&latitude_to="+lat_to+
                "&longitude_from="+lng_from+"&longitude_to="+lng_to;
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
       if (app_url === "/wave-energy/evaluate_location/"){
           $("#execution_btn_LOCATION_EVALUATION_SERVICE").click();
       }
       if (app_url === "/wave-energy/wave_forecast/"){
           $("#execution_btn_WAVE_FORECAST_SERVICE").click();
       }
       if (app_url === "/wave-energy/evaluate_area/"){
           $("#execution_btn_AREA_EVALUATION_SERVICE").click();
       }
       if (app_url === "/wave-energy/data_visualisation/") {
            $("#execution_btn_DATA_VISUALISATION_SERVICE").click();
       }

       $("#execution_status").val('starting service');

       if (app_url === "/wave-energy/data_visualisation/") {
            $(location).attr("href", app_url+"execute/"+parameters);
       }
       else{
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

});

