

var single_marker_layer;
var user_marker = {};
var first_user_marker = {};
var first_marker_layer;
var second_user_marker = {};
var second_marker_layer;
var third_user_marker ={};
var third_marker_layer;
var mode=null;

$(document).ready(function() {
    // var startdate = new Date();
    // var enddate = new Date();
    // $('#lat').val(38.06);
    // $('#lon').val(25.36);
    var startpick = $('#startdatepicker').datetimepicker({
        autoclose: true,
        pickerPosition: 'top-left',

    });

    var startpick2 = $('#startdatepicker2').datetimepicker({
        autoclose: true,
        pickerPosition: 'top-left',

    });

    var startpick3 = $('#startdatepicker3').datetimepicker({
        autoclose: true,
        pickerPosition: 'top-left',

    });

    first_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("First Marker").addTo(map);
    second_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Second Marker");
    third_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Third Marker");
    first_marker_layer = L.layerGroup(first_user_marker);
    second_marker_layer = L.layerGroup(second_user_marker);
    third_marker_layer = L.layerGroup(third_user_marker);
    map.addLayer(first_marker_layer);
    map.addLayer(second_marker_layer);
    map.addLayer(third_marker_layer);

    $('#lat').val(38.06);
    $('#lon').val(25.36);

    var endpick = $('#enddatepicker').datetimepicker({
        autoclose: true,
        pickerPosition: 'top-left',

    });


    first_user_marker.on('dragend', function (e) {

        $('#lat').val(e.target._latlng.lat);
        $('#lon').val(e.target._latlng.lng);
    });



    map.on('click', function(e){

        if (first_user_marker != undefined) {
            map.removeLayer(first_user_marker);
        }

        first_user_marker = L.marker([e.latlng.lat, e.latlng.lng], {draggable:true}).bindPopup("First Marker").addTo(map);
        first_marker_layer = L.layerGroup(first_user_marker);
        map.addLayer(first_marker_layer);
        $('#lat').val(e.latlng.lat);
        $('#lon').val(e.latlng.lng);
        first_user_marker.on('dragend', function (e) {
            $('#lat').val(e.target._latlng.lat);
            $('#lon').val(e.target._latlng.lng);
        });


    });
    // map.on('click', function(e){
    //
    //     point2_form = $("#point2_form");
    //     point3_form = $("#point3_form");
    //
    //     if (point2_form.is(":hidden")) {
    //         $('#lat').val(e.latlng.lat);
    //         $('#lon').val(e.latlng.lng);
    //     }
    //     else if (point3_form.is(":hidden")){
    //         $('#lat2').val(e.latlng.lat);
    //         $('#lon2').val(e.latlng.lng);
    //     }
    //     else {
    //         $('#lat3').val(e.latlng.lat);
    //         $('#lon3').val(e.latlng.lng);
    //     }
    //
    //     if (user_marker != undefined) {
    //         map.removeLayer(user_marker);
    //     }
    //
    //
    //
    //     user_marker = L.marker([e.latlng.lat, e.latlng.lng],  {draggable:true}).bindPopup("AS4254").addTo(map);
    //     single_marker_layer = L.layerGroup(user_marker);
    //     map.addLayer(single_marker_layer);
    //     user_marker.on('dragend', function (e) {
    //
    //         if (point2_form.is(":hidden")) {
    //             $('#lat').val(e.latlng.lat);
    //             $('#lon').val(e.latlng.lng);
    //         }
    //         else if (point3_form.is(":hidden")) {
    //             $('#lat2').val(e.latlng.lat);
    //             $('#lon2').val(e.latlng.lng);
    //         }
    //         else {
    //             $('#lat3').val(e.latlng.lat);
    //             $('#lon3').val(e.latlng.lng);
    //         }
    //     })
    //
    // });


    $("#new_point").click(function(){
        // point2_form = $("#point2_form");
        // if (point2_form.is(":hidden"))
        //   point2_form.show();
        // else
        //     $("#point3_form").show();
        $('.nav li.active').next('li').removeClass('disabled');
        var tabid = $('.nav li.active').children('a[data-toggle="pill"]').attr('href');
        $(tabid).removeClass('active');
        $(tabid).removeClass('in');
        $('.nav li.active').next('li').find('a').attr("data-toggle","pill");
        $('.nav li.active').next('li').addClass('active');
        $('.nav li.active').prev('li').removeClass('active');
        var tabid2 = $('.nav li.active').children('a[data-toggle="pill"]').attr('href');
        $(tabid2).addClass('active');
        $(tabid2).addClass('in');

        if ( tabid2 === "#point2_form"){

            if (second_user_marker != undefined) {
                map.removeLayer(second_user_marker);
            }
            var redIcon = new L.Icon({
                iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'
            });
            second_user_marker = L.marker([38.06, 25.36], {draggable:true}, {icon: redIcon}).bindPopup("Second Marker").addTo(map);
            second_user_marker.setIcon(redIcon);
            second_marker_layer = L.layerGroup(second_user_marker);
            map.addLayer(second_marker_layer);
            second_user_marker.on('dragend', function (e) {

                $('#lat2').val(e.target._latlng.lat);
                $('#lon2').val(e.target._latlng.lng);
            });
            $('#lat2').val(38.06);
            $('#lon2').val(25.36);
        }
        else if(tabid2 === "#point3_form"){
            if (third_user_marker != undefined) {
                map.removeLayer(third_user_marker);
            }
            var greenIcon = new L.Icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png'
            });
            third_user_marker = L.marker([38.06, 25.36], {draggable:true}, {icon: greenIcon}).bindPopup("Third Marker").addTo(map);
            third_user_marker.setIcon(greenIcon);
            third_marker_layer = L.layerGroup(third_user_marker);
            map.addLayer(third_marker_layer);

            third_user_marker.on('dragend', function (e) {
                $('#lat3').val(e.target._latlng.lat);
                $('#lon3').val(e.target._latlng.lng);
            });

            $('#lat3').val(38.06);
            $('#lon3').val(25.36);

        }

    });

    $('#remove_point2').click(function () {
        $('#lat2').val("");
        $('#lon2').val("");
        if (second_user_marker != undefined) {
            map.removeLayer(second_user_marker);
        }
        $("#point2_form").removeClass("in");
        $("#point2_form").removeClass("active");
        $("#point1_form").addClass("in");
        $("#point1_form").addClass("active");
        $('.nav-item').children('a[href="#point2_form"]').removeAttr('data-toggle');
        $('.nav-item').children('a[href="#point2_form"]').parent().removeClass('active');
        $('.nav-item').children('a[href="#point2_form"]').parent().addClass('disabled');
        $('.nav-item').children('a[href="#point1_form"]').parent().addClass('active');
    });


    $('#remove_point3').click(function () {
        $('#lat3').val("");
        $('#lon3').val("");
        if (third_user_marker != undefined) {
            map.removeLayer(third_user_marker);
        }
        $("#point3_form").removeClass("in");
        $("#point3_form").removeClass("active");
        $("#point1_form").addClass("in");
        $("#point1_form").addClass("active");
         $('.nav-item').children('a[href="#point3_form"]').removeAttr('data-toggle');
        $('.nav-item').children('a[href="#point3_form"]').parent().removeClass('active');
        $('.nav-item').children('a[href="#point3_form"]').parent().addClass('disabled');
        $('.nav-item').children('a[href="#point1_form"]').parent().addClass('active');
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
        lat4 = lng4 = lat5 = lng5 = '';
        start_date2 = $( "#startdatepicker2 input" ).datepicker({ dateFormat: "yy-mm-dd" }).val();
        start_date3 = $( "#startdatepicker3 input" ).datepicker({ dateFormat: "yy-mm-dd" }).val();
        start_date4 = start_date5 = '';
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