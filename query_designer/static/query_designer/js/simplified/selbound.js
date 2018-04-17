var bounds = [-90,-180,90,180];
var startdate = null;
var enddate = null;
$(document).ready(function() {
    $('#mapchoices').select2();
    $('#resolution select').select2({width: 'style'});


    var selections = [[53,10,65,30],[34,129,52,142],[12,32,29,42],[30,6,46,36]];              // configure some predifined places here

    var map, mapprev, init=false;


    /*          Set Up Maps for Modal and Preview       */
    function map_init() {
        var maplayer = 'https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.png?access_token=';
        var token = 'pk.eyJ1IjoiZ3RzYXBlbGFzIiwiYSI6ImNqOWgwdGR4NTBrMmwycXMydG4wNmJ5cmMifQ.laN_ZaDUkn3ktC7VD0FUqQ';
        var attr = 'Map data &copy;<a href="http://openstreetmap.org">OpenStreetMap</a>contributors,' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>' +
        'Imagery \u00A9 <a href="http://mapbox.com">Mapbox</a>';

        map = L.map('map').setView([0, 0], 1);
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

    $('#bounds').addClass('after-data-selection');
    /*          Set Up Maps for Modal and Preview       */
    /*          Set Up Time Pickers For Start/End Date  */
    var startpick = $('#startdatepicker').datetimepicker({autoclose: true, pickerPosition: 'top-right'});
    var endpick = $('#enddatepicker').datetimepicker({autoclose: true, pickerPosition: 'top-right'});

    startpick.on('changeDate', function(e){
        var minDate = new Date(e.date.valueOf());
        endpick.datetimepicker('setStartDate' ,minDate);
        startdate = $('#startdatepicker input').val();
        set_time_filters();
    });
    endpick.on('changeDate', function(e){
        var maxDate = new Date(e.date.valueOf());
        startpick.datetimepicker('setEndDate', maxDate);
        enddate = $('#enddatepicker input').val();
        set_time_filters();
    });
    /*          Set Up Time Pickers For Start/End Date  */

    /*          Set Up Selection Area on Map            */
    var areaSelect = L.areaSelect({
            width:450,
            height:450
    }).addTo(map);
    /*          Set Up Selection Area on Map            */
    /*          Set Up Default Selection of Map         */
    var mapselect = $('#mapchoices');
    mapselect.on('change', function(){
        var i = parseInt($('#mapchoices').val());
        if(i == -1){
            reset_map_selection();
        }
        else{
           areaSelect.setBounds([[selections[i][0],selections[i][1]],[selections[i][2],selections[i][3]]]);
            mapprev.fitBounds([[selections[i][0],selections[i][1]],[selections[i][2],selections[i][3]]]);
            // $('#mapbounds').html("SouthWest {Lat:" + selections[i][0] + ", Lng:" + selections[i][1] + "}</br>NorthEast {Lat:" + selections[i][2] + ", Lng:" + selections[i][3] + "}");
            bounds = [selections[i][0],selections[i][1],selections[i][2],selections[i][3]];
            $('#lat_min').val(bounds[0]);
            $('#lat_max').val(bounds[2]);
            $('#lon_min').val(bounds[1]);
            $('#lon_max').val(bounds[3]);
        }
    });
    /*          Set Up Default Selection of Map         */

    /*          Modal Open Button For Area Selection    */
    $('#mappreview').on('click', function(){

        $('#mapModal').on('show.bs.modal', function(){
            setTimeout(function() {
                map.invalidateSize();
            }, 10);
         });

        areaSelect.on("change", function() {
            area_bounds = this.getBounds();
        });

        $('#saveregion').on("click", function(){
            var swlat = Math.round(area_bounds.getSouthWest().lat * 1000) / 1000;
            var swlon = Math.round(area_bounds.getSouthWest().lng * 1000) / 1000;
            var nelat = Math.round(area_bounds.getNorthEast().lat * 1000) / 1000;
            var nelon = Math.round(area_bounds.getNorthEast().lng * 1000) / 1000;
            mapprev.fitBounds([[swlat,swlon],[nelat,nelon]]);
           $('#mapchoices').val('-1').prop('selected', false);
           // $('#mapbounds').html("SouthWest {Lat:" + swlat + ", Lng:" + swlon + "} </br>NorthEast {Lat:" + nelat + ", Lng:" + nelon + "}");
           bounds = [swlat,swlon,nelat,nelon];
           $('#lat_min').val(bounds[0]);
           $('#lat_max').val(bounds[2]);
           $('#lon_min').val(bounds[1]);
           $('#lon_max').val(bounds[3]);
           set_bounds_filters()
        });
    });


    $('#lat_min, #lat_max, #lon_min, #lon_max').change(function () {
        bounds = [parseFloat($('#lat_min').val()),parseFloat($('#lon_min').val()),parseFloat($('#lat_max').val()),parseFloat($('#lon_max').val())];
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

    function set_bounds_filters() {
        var latitude_dim_id = $('#selected_dimensions option[data-type="latitude"]').val();
        var longitude_dim_id = $('#selected_dimensions option[data-type="longitude"]').val();
        // QueryToolbox.filterManager.addFilter(latitude_dim_id, 'gt', bounds[0].toString());
        // QueryToolbox.filterManager.addFilter(latitude_dim_id, 'lt' , bounds[2].toString());
        // QueryToolbox.filterManager.addFilter(longitude_dim_id, 'gt' , bounds[1].toString());
        // QueryToolbox.filterManager.addFilter(longitude_dim_id, 'lt' , bounds[3].toString());
    }

    function set_time_filters() {
        var time_dim_id = $('#selected_dimensions option[data-type="time"]').val();
        // QueryToolbox.filterManager.addFilter(time_dim_id, 'gt', startdate.toString());
        // QueryToolbox.filterManager.addFilter(time_dim_id, 'lt' , enddate.toString());
        // var filters = QueryToolbox.getFilterArray();
        // for (var key in filters) {
        //     if (parseInt(time_dim_id) === filters[key].a){
        //
        //     }
        // }
    }


    function reset_map_selection() {
        mapprev.fitWorld();
        // map.setView([38, 0],4);
        map.setView([0, 0], 1);
        // mapprev.setView([0, 0], 1);
        $('#mapbounds').html("");
        $('#mapchoices').val('-1').prop('selected', false);
        $('#lat_min').val('');
        $('#lat_max').val('');
        $('#lon_min').val('');
        $('#lon_max').val('');
        bounds = [-90,-180,90,180];
    }

    reset_map_selection();

    $('#resetMapBounds').click(function () {
        reset_map_selection();
        $('#mapchoices').trigger("change");
    })

});
