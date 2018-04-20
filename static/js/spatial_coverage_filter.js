var selections = [[54, 9, 66, 32], [34, 129, 52, 142], [12, 34, 29, 42], [35, 0, 41, 30]];              // configure some predifined places here
var area_size=[[150,110],[150,100],[150,90],[150,250]];      //[height,width]
var map;
var areaSelect;
var pointSelect = {};

var mode = 'pointSelect';

// map.on('click', function(e){
//     var marker = new L.marker(e.latlng).addTo(map);
// });

function addAreaSelect() {
    if (mode ==='pointSelect') {
        mode = 'areaSelect';
        areaSelect = L.areaSelect({
            width: 150,
            height: 100
        }).addTo(map);
        // var bounds = areaSelect.getBounds();
        // $("#min_lat").val(Math.round(bounds.getSouthWest().lat * 1000) / 1000);
        // $("#max_lat").val(Math.round(bounds.getNorthEast().lat * 1000) / 1000);
        // $("#min_lon").val(Math.round(bounds.getSouthWest().lng * 1000) / 1000);
        // $("#max_lon").val(Math.round(bounds.getNorthEast().lng * 1000) / 1000);
        areaSelect.on("change", function () {
            var bounds = this.getBounds();
            $("#min_lat").val(Math.round(bounds.getSouthWest().lat * 1000) / 1000);
            $("#max_lat").val(Math.round(bounds.getNorthEast().lat * 1000) / 1000);
            $("#min_lon").val(Math.round(bounds.getSouthWest().lng * 1000) / 1000);
            $("#max_lon").val(Math.round(bounds.getNorthEast().lng * 1000) / 1000);
        });
    }
}
function removeAreaSelect() {
    areaSelect.remove();
}
function addPointSelect() {
    mode = 'pointSelect'
}
function removePointSelect() {
    if (pointSelect != undefined) {
        map.removeLayer(pointSelect);
    }
    mode = 'areaSelect'
}

function load_map() {
    map_init();
    addAreaSelect();

    var mapselect = $('#mapchoices');
    mapselect.on('change', function () {
        var i = parseInt($('#mapchoices').val());
        if (i == -1) {
            map.setView([38, 25], 5);
            areaSelect.setDimensions({width: 200, height: 150});
        }
        else {
            map.setView([selections[i][0]+(selections[i][2]-selections[i][0])/2,selections[i][1]+(selections[i][3]-selections[i][1])/2],3);
            map.fitBounds([[selections[i][0],selections[i][1]],[selections[i][2],selections[i][3]]]);
            areaSelect.setDimensions({width: area_size[i][1], height: area_size[i][0]});
        }
    });

    $('#min_lat, #min_lon, #max_lat, #max_lon').on('change', function () {
            // map.setView([selections[i][0]+(selections[i][2]-selections[i][0])/2,selections[i][1]+(selections[i][3]-selections[i][1])/2],3);
            // areaSelect.setDimensions({width: area_size[i][1], height: area_size[i][0]});
    });

}

function map_init() {
    var areaControl = L.Control.extend({
        options: {
        position: 'topleft'
        },
        onAdd: function (map) {
            var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-area');
            // var icon = $('<i class="fas fa-map-marker-alt"></i>');
            // container.append(icon);
            container.style.backgroundColor = 'white';
            container.style.width = '30px';
            container.style.height = '30px';

            return container;
        }
    });
    var pointControl = L.Control.extend({
        options: {
        position: 'topleft'
        },
        onAdd: function (map) {
            var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-point');
            container.style.backgroundColor = 'white';
            container.style.width = '30px';
            container.style.height = '30px';
            container.style.marginTop = '2px';

            return container;
        }
    });

    var maplayer = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token=';
    var token = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ';
    var attr = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors,' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>' +
        'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>';

    map = L.map('newmap').setView([38, 25], 5);
    L.tileLayer(maplayer + token, {
        attribution: attr,
        maxZoom: 18
    }).addTo(map);

    map.addControl(new areaControl());
    $('.leaflet-control-area').append('<a role="button"><i> </i></a>');
    $('.leaflet-control-area i').addClass('fa fa-square');

    map.addControl(new pointControl());
    $('.leaflet-control-point').append('<a role="button"><i> </i></a>');
    $('.leaflet-control-point i').addClass('fa fa-map-marker');

    $('.leaflet-control-area').click(function () {
        addAreaSelect();
        removePointSelect();
    });
    $('.leaflet-control-point').click(function () {
        event.stopPropagation();
        removeAreaSelect();
        addPointSelect();
    });

    map.on('click', function(e){
        if(mode==='pointSelect'){
            // alert(mode);
            if (pointSelect != undefined) {
                map.removeLayer(pointSelect);
            }
            //Add a marker to show where you clicked.
            var lat = e.latlng.lat;
            var lon = e.latlng.lng;
             pointSelect = L.marker([lat,lon]).addTo(map);
            $("#min_lat").val(Math.round(lat * 1000) / 1000);
            $("#max_lat").val(Math.round(lat * 1000) / 1000);
            $("#min_lon").val(Math.round(lon * 1000) / 1000);
            $("#max_lon").val(Math.round(lon * 1000) / 1000);
        }
    });
}



$( "#newmap" ).closest('.modal').on('shown.bs.modal', function (e) {
    load_map();
});
$( "#newmap" ).closest('.popover').on('shown.bs.popover', function (e) {
    map_init();
});
$( "#newmap" ).closest('.collapse').on('shown.bs.collapse', function (e) {
    map_init();
});

$( "#newmap" ).ready(function (e) {
    var inModal = this.closest('.modal').length === 0;
    var inPopover = this.closest('.popover').length === 0;
    var inCollapse = this.closest('.collapse').length === 0;
    if (inModal || inPopover || inCollapse){
        map_init();
    }
});

$('.row').ready( function () {
    $('#choices select').select2();
});

$( "#newmap" ).parent().find('label').css("line-height", "0");