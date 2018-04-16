var selections = [[54, 9, 66, 32], [34, 129, 52, 142], [12, 34, 29, 42], [35, 0, 41, 30]];              // configure some predifined places here
var area_size=[[150,110],[150,100],[150,90],[150,250]]      //[height,width]
var bounds = [0, 0, 30, 30];

var startdate, enddate;
var map, mapprev, init = false;

function load_map() {

    map_init();
    //Create an element when the document is ready, hide it in a div, move it wherever is needed, show it.
    $("#hiddenelement").hide();

    //Create area select.
    var areaSelect = L.areaSelect({
        width: 200,
        height: 150
    }).addTo(map);
    //Add area_select value to the hidden inputs.Use the inputs later onSubmit.
    areaSelect.on("change", function() {
        var bounds = this.getBounds();
        $("#min_lat").val(bounds.getSouthWest().lat);
        $("#max_lat").val(bounds.getNorthEast().lat);
        $("#min_lon").val(bounds.getSouthWest().lng);
        $("#max_lon").val(bounds.getNorthEast().lng);
    });

    /*          Set Up Default Selection of Map         */
    var mapselect = $('#mapchoices');
    mapselect.on('change', function () {
        var i = parseInt($('#mapchoices').val());
        if (i == -1) {
            map.setView([38, 25], 5);
            areaSelect.setDimensions({width: 200, height: 150});
        }
        else {
            map.setView([selections[i][0]+(selections[i][2]-selections[i][0])/2,selections[i][1]+(selections[i][3]-selections[i][1])/2],3)
            areaSelect.setDimensions({width: area_size[i][1], height: area_size[i][0]});
        }
    });

}


/*          Set Up Maps for Modal and Preview       */
function map_init() {
    var maplayer = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token=';
    var token = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ';
    var attr = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors,' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>' +
        'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>';

    map = L.map('hiddenmap').setView([38, 25], 5);
    L.tileLayer(maplayer + token, {
        attribution: attr,
        maxZoom: 18
    }).addTo(map);
    init = true;
}


function move_map(m_from,m_to) {
    $(m_from).appendTo(m_to);
    alert("Map moved!")
}


