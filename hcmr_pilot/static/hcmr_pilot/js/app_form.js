

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

        point2_form = $("#point2_form");
        point3_form = $("#point3_form");

        if (point2_form.is(":hidden")) {
            $('#lat').val(e.latlng.lat);
            $('#lon').val(e.latlng.lng);
        }
        else if (point3_form.is(":hidden")){
            $('#lat2').val(e.latlng.lat);
            $('#lon2').val(e.latlng.lng);
        }
        else {
            $('#lat3').val(e.latlng.lat);
            $('#lon3').val(e.latlng.lng);
        }

        if (user_marker != undefined) {
            map.removeLayer(user_marker);
        }


        user_marker = L.marker([e.latlng.lat, e.latlng.lng],  {draggable:true}).bindPopup("AS4254").addTo(map);
        single_marker_layer = L.layerGroup(user_marker);
        map.addLayer(single_marker_layer);
        user_marker.on('dragend', function (e) {

            if (point2_form.is(":hidden")) {
                $('#lat').val(e.latlng.lat);
                $('#lon').val(e.latlng.lng);
            }
            else if (point3_form.is(":hidden")) {
                $('#lat2').val(e.latlng.lat);
                $('#lon2').val(e.latlng.lng);
            }
            else {
                $('#lat3').val(e.latlng.lat);
                $('#lon3').val(e.latlng.lng);
            }
        })

    });
    $("#new_point").click(function(){
        point2_form = $("#point2_form");
        if (point2_form.is(":hidden"))
          point2_form.show();
        else
            $("#point3_form").show();
    });


    $("#run-service-btn").click(function () {
        var lat = $('#lat').val();
        var lng = $("#lon").val();
        var oil_volume = $("#oil_volume").val();
        var oil_density = $("#oil_density").val();
        var time_interval = $("#time_interval").val();
        var simulation_length = $("#simulation_length").val();
        var duration = $("#vis_duration").val();
        lat2 = $('#lat2').val();
        lng2 = $('#lon2').val();
        lat3 = $('#lat3').val();
        lng3 = $('#lon3').val();
        lat4 = lng4 = lat5 = lng5 = ''
        start_date2 = $( "#startdatepicker2 input" ).datepicker({ dateFormat: "yy-mm-dd" }).val();
        start_date3 = $( "#startdatepicker3 input" ).datepicker({ dateFormat: "yy-mm-dd" }).val();
        start_date4 = start_date5 = ''
        duration2 = $("#vis_duration2").val();
        duration3 = $("#vis_duration3").val();
        duration4 = duration5 = '';
        var oil_volume2 = $("#oil_volume2").val();
        var oil_volume3 = $("#oil_volume3").val();
        var oil_volume4 = oil_volume5 = '';

        var start_date = $( "#startdatepicker input" ).datepicker({ dateFormat: "yy-mm-dd" }).val();
        var enddate = $( "#enddatepicker input" ).datepicker({ dateFormat: "yy-mm-dd" }).val();

        var url = "http://localhost:8000/oilspill/process/?csrfmiddlewaretoken=LlLKJ7OlQGdAUeWOeOT52n" +
            "Y6Z5dlBNu9OqDB0X2nu6egRBPUrbY5PiTWWUxTF1tg"+
            "&latitude1="+lat+
            "&longitude1="+lng+
            "&start_date1="+start_date+
            "&duration1="+duration+
            "&latitude2="+lat2+
            "&longitude2="+lng2+
            "&start_date2="+start_date2+
            "&duration2="+duration2+
            "&latitude3="+lat3+
            "&longitude3="+lng3+
            "&start_date3="+start_date3+
            "&duration3="+duration3+
            "&latitude4="+lat4+
            "&longitude4="+lng4+
            "&start_date4="+start_date4+
            "&duration4="+duration4+
            "&latitude5="+lat5+
            "&longitude5="+lng5+
            "&start_date5="+start_date5+
            "&duration5="+duration5+
            "&end_date="+enddate+
            "&oil_volume1="+oil_volume+
            "&oil_volume2="+oil_volume2+
            "&oil_volume3="+oil_volume3+
            "&oil_volume4="+oil_volume4+
            "&oil_volume5="+oil_volume5+
            "&oil_density="+oil_density+
            "&simulation_length="+simulation_length+
            "&time_interval="+time_interval

        console.log(url)
        window.location.replace(url)
    });

});