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

        map = L.map('map');
        // map.setView([0, 0], 0);
        map.fitWorld();
        map.setMinZoom(1);

        L.tileLayer(maplayer + token, {
            attribution: attr,
            maxZoom: 18,
            // continuousWorld: false,
            // noWrap: true,
        }).addTo(map);

        init = true;
        mapprev = L.map('mappreview',{
            zoomControl: false,
            // continuousWorld: false,
            // noWrap: true,
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

    function set_bounds_filters() {
        var latitude_dim_id = $('#selected_dimensions option[data-type="latitude"]').val();
        var longitude_dim_id = $('#selected_dimensions option[data-type="longitude"]').val();
    }

    function set_time_filters() {
        var time_dim_id = $('#selected_dimensions option[data-type="time"]').val();
    }

    function reset_map_selection() {
        mapprev.fitWorld();

        // map.setView([0, 0], 0);
        //removes existing area-select
        $(".leaflet-interactive").remove();
        create_new_area_select([[-90,-180],[90,180]]);
        $('#lat_min').val("");
        $('#lat_max').val("");
        $('#lon_min').val("");
        $('#lon_max').val("");

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
        mapprev.fitBounds(area_select_bounds);
        // $('#mapbounds').html("SouthWest {Lat:" + selections[i][0] + ", Lng:" + selections[i][1] + "}</br>NorthEast {Lat:" + selections[i][2] + ", Lng:" + selections[i][3] + "}");
        bounds = [area_select_bounds[0][0],area_select_bounds[0][1],area_select_bounds[1][0],area_select_bounds[1][1]];
        $('#lat_min').val(bounds[0]);
        $('#lat_max').val(bounds[2]);
        $('#lon_min').val(bounds[1]);
        $('#lon_max').val(bounds[3]);

    }



    // $("#mapchoices option:contains('Choose Predefined')").attr("disabled","disabled");
    $('#mapchoices').select2({
        placeholder: "Choose Predefined",
        allowClear: true
    });
    $('#resolution select').select2({width: 'style'});

    map_init();


    //
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

    /*          Set Up Default Selection of Map         */
    var mapselect = $('#mapchoices');
    mapselect.on('change', function(){
        var i = parseInt($('#mapchoices').val());
        if(isNaN(i)){
            // reset_map_selection();
        }
        else{
            create_new_area_select([[selections[i][0],selections[i][1]],[selections[i][2],selections[i][3]]]);
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


        $('#saveregion').on("click", function(){
            $('#mapchoices').val(null).trigger('change');
            area_bounds = areaSelect.getBounds();
            var swlat = Math.round(area_bounds.getSouthWest().lat * 10000) / 10000;
            var swlon = Math.round(area_bounds.getSouthWest().lng * 10000) / 10000;
            var nelat = Math.round(area_bounds.getNorthEast().lat * 10000) / 10000;
            var nelon = Math.round(area_bounds.getNorthEast().lng * 10000) / 10000;
            mapprev.fitBounds([[swlat,swlon],[nelat,nelon]]);
           // $('#mapchoices').val('-1').prop('selected', false);
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
        // $('#mapchoices option[value=-1]').prop('disabled', 'enabled');
        // $('#mapchoices').val(-1);
        // $('#mapchoices').trigger('change');
        $('#mapchoices').val(null).trigger('change');
        if ((!isNaN($('#lat_min').val())&&($('#lat_min').val()!=="")) && (!isNaN($('#lat_max').val())&&($('#lat_max').val()!=="")) && (!isNaN($('#lon_min').val())&&($('#lon_min').val()!=="")) && (!isNaN($('#lon_max').val())&&($('#lon_max').val()!==""))) {
            bounds = [parseFloat($('#lat_min').val()), parseFloat($('#lon_min').val()), parseFloat($('#lat_max').val()), parseFloat($('#lon_max').val())];
            $(".leaflet-interactive").remove();
            create_new_area_select([[parseFloat($('#lat_min').val()), parseFloat($('#lon_min').val())], [parseFloat($('#lat_max').val()), parseFloat($('#lon_max').val())]]);
        }
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

    reset_map_selection();


    $('#resetMapBounds').click(function () {
        reset_map_selection();
        $('#mapchoices').val(null).trigger('change');
        // $('#mapchoices').trigger("change");
    })

     $('#resetDates').click(function () {
         $('#startdatepicker input').val('');
         $('#enddatepicker input').val('');
         startdate = null;
         enddate =null;
    })

});