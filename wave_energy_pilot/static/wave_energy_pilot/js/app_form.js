
var buoys_layer;
var single_marker_layer;
var user_marker = {};
var buoys_markers = [];
var mode=null;
$(document).ready(function() {
    
    function create_buoys_dataset_dict() {
        var buoys_dict = [];
        $('.buoy').each(function(i, obj) {

            var my_list = [];
            var buoy_id = $(this).data("id");
            var dataset_id = $(this).data("dataset_id");
            my_list.push(buoy_id, dataset_id);
            buoys_dict.push(my_list);
        })
        return buoys_dict;
    }

    var buoys_dict = create_buoys_dataset_dict();

    function create_buoys_plane(){
        var buoys_plane = [];
        $('.buoy').each(function(i, obj) {
            var buoy_id = $(this).data("id");
            var buoy_lat = $(this).data("lat");
            var buoy_lon = $(this).data("lon");
            var buoy = [buoy_id, buoy_lat, buoy_lon];
            buoys_plane.push(buoy);
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


    $('#select_app').dropdown();
    $('#select_dataset').dropdown();
    $('.ui.dropdown').dropdown();
    $('#select_dataset_wave_resource_assessment_single').dropdown();
    $('#select_dataset_wave_resource_assessment_area').dropdown();
    $('#select_dataset_data_visualisation').dropdown();

    var dataset_selection = $('#select_dataset_data_visualisation :selected').val();

    $('#'+dataset_selection+'-variables').show();

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


    function erase_user_marker(){

        var redIcon = new L.Icon({
          iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'
        });
        for(var i = 0; i < buoys_markers.length; i++){
            buoys_markers[i].setIcon(redIcon);
        }
        $("#select_dataset_data_visualisation .item").each(function() {
            if($(".item").hasClass("disabled")) {

                $(".item").removeClass("disabled");
            }
        });
        var selected_buoy = this.getPopup().getContent();
        var dataset_id = -1;
        for(var i = 0; i < buoys_dict.length; i++){
            if(buoys_dict[i][0] === selected_buoy){
                dataset_id = buoys_dict[i][1];
                break;
            }
        }

        //select the dataset which the buoy belongs
        var dataset_title = $(`#select_dataset_data_visualisation .item[data-id="${dataset_id}"]`).data("title");
        $("#select_dataset_data_visualisation").dropdown("set selected", [`${dataset_title}`]);


        $("#select_dataset_data_visualisation .item").each(function() {

            if ($(this).data("id") != dataset_id){
                var dropwdown_id = $(this).data("id");
               $(`.item[data-id="${dropwdown_id}"]`).addClass("disabled item");
            }
        });
        var newIcon = new L.Icon({iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png'});
        this.setIcon(newIcon);

        $('#lat').val(this.getLatLng().lat);
        $('#lon').val(this.getLatLng().lng);

        if(user_marker != undefined){
            map.removeLayer(user_marker);
        }
    }

    $(function () {
        $('.app-selector').change(function () {

            //Wave Forecast Scenario
            if ($('.app-selector :selected').val() == "Wave_Forecast") {
                $('.dataset-selector').hide();
                $('.coverage-date-filters').show();
                $('#wave-forecast-results').show();
                $('.single-spatial-selection').show();

                map.on('click', function(e){
                    if (mode == "location") {
                        $('#lat').val(e.latlng.lat);
                        $('#lon').val(e.latlng.lng);

                        if (user_marker != undefined) {
                            map.removeLayer(user_marker);
                        }

                        user_marker = L.marker([e.latlng.lat, e.latlng.lng]).bindPopup("AS4254").addTo(map);
                        single_marker_layer = L.layerGroup(user_marker);
                        map.addLayer(single_marker_layer);
                        user_marker.on('dragend', function (e) {
                            // alert(e.target._latlng);
                             $('#lat').val(e.target._latlng.lat);
                             $('#lon').val(e.target._latlng.lng);
                        })
                    }
                 });

                /* Set Up Time Pickers For Start/End Date  */
                set_forecast_timeframe();
            }
            else{
                $('.single-spatial-selection').hide();
                $('.dataset-selector').show();
                $('.coverage-date-filters').show();
                $('#wave-forecast-results').hide();
                $('#startdatepicker input').val('');
                $('#enddatepicker input').val('');
                // $('#enddatepicker').datepicker('remove');
                // $('#startdatepicker').datepicker('remove');
                startdate = null;
                enddate = null;

            }
            if ($('.app-selector :selected').val() == "Wave_Resource_Assessment_area"){
                mode = "area";
                $("#map").css("cursor", "grab");
                $('.wave_resource_assessment_area_dropdown').show();
                $('.spatial-selection').show();
                $('#wave-atlas-results').show();
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

                $('#lat_min, #lat_max, #lon_min, #lon_max').change(function () {
                    bounds = [parseFloat($('#lat_min').val()),parseFloat($('#lon_min').val()),parseFloat($('#lat_max').val()),parseFloat($('#lon_max').val())];
                    $(".leaflet-interactive").remove();
                    create_new_area_select([[parseFloat($('#lat_min').val()),parseFloat($('#lon_min').val())],[parseFloat($('#lat_max').val()),parseFloat($('#lon_max').val())]]);
                });
                set_app_dataset_date_pickers("select_dataset_wave_resource_assessment_area");
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
                $('.data_visualisation').show();
                $('.single-spatial-selection').show();
                $('#data-visualisation-results').show();
                $('.variable-selector').show();

                create_buoys_plane();

                map.on('click', function(e) {
                    if (mode == "location"){
                        $('#lat').val(e.latlng.lat);
                        $('#lon').val(e.latlng.lng);

                        //make again the buoys layer red
                        var redIcon = new L.Icon({iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'});
                        for(var i = 0; i < buoys_markers.length; i++)
                            buoys_markers[i].setIcon(redIcon);

                        if (user_marker != undefined) {
                            map.removeLayer(user_marker);
                        }

                        $("#select_dataset_data_visualisation .item").each(function() {
                            if($(".item").hasClass("disabled")) {
                                $(".item").removeClass("disabled");
                            }
                        });

                        user_marker = L.marker([e.latlng.lat, e.latlng.lng], {draggable:true}).bindPopup("AS4254").addTo(map);
                        single_marker_layer = L.layerGroup(user_marker);
                        map.addLayer(single_marker_layer);
                        user_marker.on('dragend', function (e) {

                             $('#lat').val(e.target._latlng.lat);
                             $('#lon').val(e.target._latlng.lng);
                        })
                    }
                 });
                set_app_dataset_date_pickers("select_dataset_data_visualisation");
            }
            else{
                $('.data_visualisation').hide();
                $('#data-visualisation-results').hide();
                $('.variable-selector').hide();
                // $('.single-spatial-selection').hide();

                if(map.hasLayer(buoys_layer)) {
                    map.removeLayer(buoys_layer);
                }
            }
             if ($('.app-selector :selected').val() == "Wave_Resource_Assessment_single"){
                 $('.wave_resource_assessment_single_dropdown').show();
                 $('#wave-resource-assessment').show();
                 $('.single-spatial-selection').show();

                 map.on('click', function(e){
                    if (mode == "location") {
                        $('#lat').val(e.latlng.lat);
                        $('#lon').val(e.latlng.lng);

                        if (user_marker != undefined) {
                            map.removeLayer(user_marker);
                        }

                        $("#select_dataset_data_visualisation .item").each(function() {
                            if($(".item").hasClass("disabled")) {
                                $(".item").removeClass("disabled");
                            }
                        });

                        user_marker = L.marker([e.latlng.lat, e.latlng.lng],  {draggable:true}).bindPopup("AS4254").addTo(map);
                        single_marker_layer = L.layerGroup(user_marker);
                        map.addLayer(single_marker_layer);
                        user_marker.on('dragend', function (e) {

                             $('#lat').val(e.target._latlng.lat);
                             $('#lon').val(e.target._latlng.lng);
                        })
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
       $('#'+app_selector).change(function () {
           $('.variables-selector').hide();
           var dataset_selection = $('#'+app_selector).dropdown('get text');
           var dataset_id = $(`.item[data-title="${dataset_selection}"]`).data("id");

           $('#'+dataset_id+'-variables').show();
           $('.dataset').each(function (i, obj) {

               if ($(this).data("title") == dataset_selection){

                   var startdate = new Date($(this).data("startdate"));
                   var enddate = new Date($(this).data("enddate"));
                   // startdate.setDate();
                    var startpick = $('#startdatepicker').datetimepicker({
                        autoclose: true,
                        pickerPosition: 'top-left',
                        startDate: startdate,
                        endDate: enddate,
                    });
                    $('#startdatepicker').datetimepicker("update", startdate);


                    // enddate.setDate();
                    var endpick = $('#enddatepicker').datetimepicker({
                        autoclose: true,
                        pickerPosition: 'top-left',
                        startDate: startdate,
                        endDate: enddate
                    });
                    $('#enddatepicker').datetimepicker("update", enddate);
               }
           })
       })
   }

   $("#run-service-btn").click(function () {
       alert("pathsa to koumpi yeaaa");
   })


});

