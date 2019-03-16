var bounds = [-90,-180,90,180];
var startdate = null;
var enddate = null;

var selections = [[53,9,66,31],[32,125,53,144],[12,32,30,45],[30,-6,46,37]];              // configure some predifined places here
var areaSelect;
var map, mapprev, init=false;
var area_bounds;


$(document).ready(function() {
     /*          Set Up Maps for Modal and Preview       */
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


    map_init();
    // create_new_area_select([[29.2575,-24.2578],[49.479,37.0898]]);

    //
    $('#bounds').addClass('after-data-selection');
    /*          Set Up Maps for Modal and Preview       */
    //Change Lan, Lon values from user's selection area

    $('.leaflet-edit-move').click(function(){
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

    $('.leaflet-edit-resize').click(function(){
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

    $('#resetMapBounds').click(function () {
        reset_map_selection();
        $('#mapchoices').val(null).trigger('change');
    })

     $('#resetDates').click(function () {
         $('#startdatepicker input').val('');
         $('#enddatepicker input').val('');
         startdate = null;
         enddate =null;
    })

});