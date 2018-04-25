
    var selections = [[53, 10, 65, 30], [34, 129, 52, 142], [12, 32, 29, 42], [30, 6, 46, 36]];              // configure some predifined places here
    var bounds = [0, 0, 30, 30];
    var startdate, enddate;
    var map, mapprev, init = false;
function load_map() {


    /*          Set Up Maps for Modal and Preview       */
    function map_init() {
        var maplayer = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token=';
        var token = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ';
        var attr = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors,' +
            '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>' +
            'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>';

        map = L.map('hiddenmap').setView([38, 0], 4);
        L.tileLayer(maplayer + token, {
            attribution: attr,
            maxZoom: 18
        }).addTo(map);
        init = true;


    }

    map_init();


    /*          Set Up Selection Area on Map            */
    // var areaSelect = L.areaSelect({
    //     width: 500,
    //     height: 200
    // }).addTo(map);
    // var areaSelect;
    // /*          Set Up Selection Area on Map            */
    // /*          Set Up Default Selection of Map         */
    // var mapselect = $('#mapchoices');
    // mapselect.on('change', function () {
    //     var i = parseInt($('#mapchoices').val());
    //     if (i == -1) {
    //         map.setView([38, 0], 4);
    //         $('#mapbounds').html("");
    //         bounds = [0, 0, 30, 30];
    //     }
    //     else {
    //         areaSelect.setBounds([[selections[i][0], selections[i][1]], [selections[i][2], selections[i][3]]]);
    //         $('#mapbounds').html("SouthWest {Lat:" + selections[i][0] + " Lng:" + selections[i][1] + "} <br>NorthEast {Lat:" + selections[i][2] + " Lng:" + selections[i][3] + "}");
    //         bounds = [selections[i][0], selections[i][1], selections[i][2], selections[i][3]];
    //     }
    // });
    /*          Set Up Default Selection of Map         */

    /*          Modal Open Button For Area Selection    */
    /*          Modal Open Button For Area Selection    */

}


function move_map() {
    $("#hiddenmap").appendTo("#newmap");

}