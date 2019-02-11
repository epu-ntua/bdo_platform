

var single_marker_layer;
var user_marker = {};
var mode=null;

$(document).ready(function() {
    // var startdate = new Date();
    // var enddate = new Date();

    var startpick = $('#startdatepicker').datetimepicker({
        autoclose: true,
        pickerPosition: 'top-left',

    });


    var endpick = $('#enddatepicker').datetimepicker({
        autoclose: true,
        pickerPosition: 'top-left',

    });

    map.on('click', function(e){

        $('#lat').val(e.latlng.lat);
        $('#lon').val(e.latlng.lng);

        if (user_marker != undefined) {
            map.removeLayer(user_marker);
        }


        user_marker = L.marker([e.latlng.lat, e.latlng.lng],  {draggable:true}).bindPopup("AS4254").addTo(map);
        single_marker_layer = L.layerGroup(user_marker);
        map.addLayer(single_marker_layer);
        user_marker.on('dragend', function (e) {

             $('#lat').val(e.target._latlng.lat);
             $('#lon').val(e.target._latlng.lng);
        })

    });

    $("#run-service-btn").click(function () {
        var lat = $('#lat').val();
        var lng = $("#lon").val();
        var oil_volume = $("#oil_volume").val();
        var oil_density = $("#oil_density").val();
        var time_interval = $("#time_interval").val();
        var simulation_length = $("#simulation_length").val();
        var duration = $("#vis_duration").val();

        var start_date = $( "#startdatepicker input" ).datepicker({ dateFormat: "yy-mm-dd" }).val();
        var enddate = $( "#enddatepicker input" ).datepicker({ dateFormat: "yy-mm-dd" }).val();

        var url = "http://localhost:8000/oilspill/process/?csrfmiddlewaretoken=LlLKJ7OlQGdAUeWOeOT52n" +
            "Y6Z5dlBNu9OqDB0X2nu6egRBPUrbY5PiTWWUxTF1tg&latitude1="+lat+
            "&longitude1="+lng+
            "&start_date1="+start_date+
            "&end_date="+enddate+
            "&duration1="+duration+
            "&oil_volume1="+oil_volume+
            "&oil_density="+oil_density+
            "&simulation_length="+simulation_length+
            "&time_interval="+time_interval
        alert(url);


   });

});