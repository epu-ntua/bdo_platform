



var buoys_layer;
var single_marker_layer;
var user_marker = {};
$(document).ready(function() {

    function create_buoys_plane(){
        var buoys_plane = [];
        $('.buoy').each(function(i, obj) {
            var buoy_id = $(this).data("id");
            var buoy_lat = $(this).data("lat");
            var buoy_lon = $(this).data("lon");
            var buoy = [buoy_id, buoy_lat, buoy_lon];
            buoys_plane.push(buoy);
        });

        var buoys_markers = [];
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

    $('#select_app')
      .dropdown()
    ;

    $('#select_dataset')
      .dropdown()
    ;

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
        // alert(this.getLatLng().lat);
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
                $('.coverage-date-filters').hide();
                $('#wave-forecast-results').show();


                map.on('click', function(e){

                    $('#lat').val(e.latlng.lat);
                    $('#lon').val(e.latlng.lng);

                    if(user_marker != undefined){
                        map.removeLayer(user_marker);
                    }

                    user_marker = L.marker([e.latlng.lat, e.latlng.lng]).bindPopup("AS4254").addTo(map);
                    single_marker_layer =  L.layerGroup(user_marker);
                    map.addLayer(single_marker_layer);
                 });

            }
            else{
                $('.dataset-selector').show();
                $('.coverage-date-filters').show();
                $('#wave-forecast-results').hide();

            }
            if ($('.app-selector :selected').val() == "Wave_Resource_Assessment_area"){
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

            }
            else {
                $('#wave-atlas-results').hide();
                $('.spatial-selection').hide();
                // map.removeLayer(areaSelect);

            }

            if ($('.app-selector :selected').val() == "Data_Visualisation"){
                $('.single-spatial-selection').show();
                $('#data-visualisation-results').show();
                $('.variable-selector').show();

                create_buoys_plane();

                // var user_marker = {};
                map.on('click', function(e){

                    $('#lat').val(e.latlng.lat);
                    $('#lon').val(e.latlng.lng);

                    if(user_marker != undefined){
                        map.removeLayer(user_marker);
                    }

                    user_marker = L.marker([e.latlng.lat, e.latlng.lng]).bindPopup("AS4254").addTo(map);
                    single_marker_layer =  L.layerGroup(user_marker);
                    map.addLayer(single_marker_layer);
                 });

            }
            else{
               $('#data-visualisation-results').hide();
               $('.variable-selector').hide();
               $('.single-spatial-selection').hide();

                // alert("edw");
                if(map.hasLayer(buoys_layer)) {
                    // alert("edw2");
                    map.removeLayer(buoys_layer);
                }

            }

             if ($('.app-selector :selected').val() == "Wave_Resource_Assessment_single"){
                $('#wave-resource-assessment').show();
                $('.single-spatial-selection').show();

                // var user_marker = {};
                map.on('click', function(e){

                    $('#lat').val(e.latlng.lat);
                    $('#lon').val(e.latlng.lng);

                    if(user_marker != undefined){
                        map.removeLayer(user_marker);
                    }
                    user_marker = L.marker([e.latlng.lat, e.latlng.lng]).bindPopup("AS4254").addTo(map);
                    single_marker_layer =  L.layerGroup(user_marker);
                    map.addLayer(single_marker_layer);
                 });

            }
            else {
                 $('#wave-resource-assessment').hide();
             }
        })
    })




});

