$(document).ready(function() {
    var selections = [[53,10,65,30],[34,129,52,142],[12,32,29,42],[30,6,46,36]];              // configure some predifined places here
    var bounds = [0,0,30,30];
    var startdate, enddate;
    var map, mapprev, init=false;

    /*          Set Up Html for Map Selection           */
    var seldiv = document.getElementById('mapbtn');
    var regbut = document.createElement('button');
    regbut.setAttribute('class','btn btn-primary btn-xs');
    regbut.setAttribute('id', 'selbutton');
    regbut.setAttribute('data-toggle','modal');
    regbut.setAttribute('data-target','#mapModal');
    regbut.innerHTML = "Choose Region";
    seldiv.appendChild(regbut);

    seldiv = document.getElementById('fetch');
    regbut = document.createElement('button');
    regbut.setAttribute('class','btn btn-primary');
    regbut.setAttribute('id', 'project');
    regbut.innerHTML = "Project";
    seldiv.appendChild(regbut);
    /*          Set Up Html for Map Selection           */

    /*          Set Up Maps for Modal and Preview       */
    function map_init() {
        var maplayer = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token=';
        var token = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ';
        var attr = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors,' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>' +
        'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>';

        map = L.map('map').setView([38, 0], 4);
        L.tileLayer(maplayer + token, {
        attribution: attr,
        maxZoom: 18
        }).addTo(map);
        init = true;

        mapprev = L.map('mappreview',{
            zoomControl: false
            }).setView([0, 0], 0);
        mapprev.fitWorld();
        L.tileLayer(maplayer + token).addTo(mapprev);
        mapprev.dragging.disable();
        mapprev.touchZoom.disable();
        mapprev.doubleClickZoom.disable();
        mapprev.scrollWheelZoom.disable();
        mapprev.boxZoom.disable();
        mapprev.keyboard.disable();
    }

    map_init();
    /*          Set Up Maps for Modal and Preview       */
    /*          Set Up Time Pickers For Start/End Date  */
    var startpick = $('#startdatepicker').datetimepicker({autoclose: true});
    var endpick = $('#enddatepicker').datetimepicker({autoclose: true});

    startpick.on('changeDate', function(e){
        var minDate = new Date(e.date.valueOf());
        endpick.datetimepicker('setStartDate' ,minDate);
        startdate = minDate;
    });
    endpick.on('changeDate', function(e){
        var maxDate = new Date(e.date.valueOf());
        startpick.datetimepicker('setEndDate', maxDate);
        enddate = maxDate;
    });
    /*          Set Up Time Pickers For Start/End Date  */

    /*          Set Up Selection Area on Map            */
    var areaSelect = L.areaSelect({
            width:500,
            height:200
    }).addTo(map);
    /*          Set Up Selection Area on Map            */
    /*          Set Up Default Selection of Map         */
    var mapselect = $('#mapchoices');
    mapselect.on('change', function(){
        var i = parseInt($('#mapchoices').val());
        if(i == -1){
            mapprev.fitWorld();
            map.setView([38, 0],4);
            $('#mapbounds').html("");
            bounds = [0,0,30,30];
        }
        else{
           areaSelect.setBounds([[selections[i][0],selections[i][1]],[selections[i][2],selections[i][3]]]);
            mapprev.fitBounds([[selections[i][0],selections[i][1]],[selections[i][2],selections[i][3]]]);
            $('#mapbounds').html("SouthWest {Lat:" + selections[i][0] + " Lng:" + selections[i][1] + "} <br>NorthEast {Lat:" + selections[i][2] + " Lng:" + selections[i][3] + "}");
            bounds = [selections[i][0],selections[i][1],selections[i][2],selections[i][3]];
        }
    });
    /*          Set Up Default Selection of Map         */

    /*          Modal Open Button For Area Selection    */
    $('#selbutton').on('click', function(){

        $('#mapModal').on('show.bs.modal', function(){
            setTimeout(function() {
                map.invalidateSize();
            }, 10);
         });

        areaSelect.on("change", function() {
            bounds = this.getBounds();
        });

        $('#saveregion').on("click", function(){
            var swlat = bounds.getSouthWest().lat;
            var swlon = bounds.getSouthWest().lng;
            var nelat = bounds.getNorthEast().lat;
            var nelon = bounds.getNorthEast().lng;
            mapprev.fitBounds([[swlat,swlon],[nelat,nelon]]);
           $('#closemodal').click();
           $('#mapchoices').val('null').prop('selected', false);
           $('#mapbounds').html("SouthWest {Lat:" + swlat + " Lng:" + swlon + "} <br>NorthEast {Lat:" + nelat + " Lng:" + nelon + "}");
           bounds = [swlat,swlon,nelat,nelon];
        });
    });
    /*          Modal Open Button For Area Selection    */

    $('#project').on('click', function(){
        console.log(bounds);
        console.log(startdate, enddate);
        QueryToolbox.filterManager.addFilter('lat', 'gt' , bounds[0].toString());
        QueryToolbox.filterManager.addFilter('lng', 'gt' , bounds[1].toString());
        QueryToolbox.filterManager.addFilter('lat', 'lt' , bounds[2].toString());
        QueryToolbox.filterManager.addFilter('lng', 'lt' , bounds[3].toString());
        // startdate and enddate must be transposed to match database format
        QueryToolbox.filterManager.addFilter('timestamp', 'gt' , startdate.toString());
        QueryToolbox.filterManager.addFilter('timestamp', 'lt' , enddate.toString());
    });

});
