



var buoys_layer;

$(document).ready(function() {

     function map_init() {
        var maplayer = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token=';
        var token = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ';
        var attr = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors,' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>' +
        'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>';

        map = L.map('map').setView([38, 25], 5);

        L.tileLayer(maplayer + token, {
            attribution: attr,
            maxZoom: 18,

        }).addTo(map);

        init = true;

    }

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
        for (var i = 0; i < buoys_plane.length; i++){
            marker = new L.marker([buoys_plane[i][1],buoys_plane[i][2]]).bindPopup(buoys_plane[i][0]);
            buoys_markers.push(marker);
        }
        buoys_layer = L.layerGroup(buoys_markers);

        // alert(map.hasLayer(buoys_layer));
        map.addLayer(buoys_layer);
        // alert(map.hasLayer(buoys_layer));
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


    $(function () {
        $('.app-selector').change(function () {

            if ($('.app-selector :selected').val() == "Wave_Forecast") {

                $('.dataset-selector').hide();
                $('.coverage-date-filters').hide();
                $('#wave-forecast-results').show();
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
                map.remove();
                map_init();
            }

            if ($('.app-selector :selected').val() == "Data_Visualisation"){
                $('.single-spatial-selection').show();
                $('#data-visualisation-results').show();
                $('.variable-selector').show();

                create_buoys_plane();

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

            }
            else {
                 $('#wave-resource-assessment').hide();


             }
        })
    })

    $(".leaflet-marker-icon").click(function () {
        $('#lat').val();
        $('#lon').val();
    })

});

