

var single_marker_layer;
var user_marker = {};
var mode=null;

let MAX_LON_MEDITERRANEAN = 36;
let MIN_LON_MEDITERRANEAN = -7;
let MAX_LAT_MEDITERRANEAN = 45.75;
let MIN_LAT_MEDITERRANEAN = 30.25;

let MAX_LON_AEGEAN_IONIAN = 30;
let MIN_LON_AEGEAN_IONIAN = 19.5;
let MAX_LAT_AEGEAN_IONIAN = 41;
let MIN_LAT_AEGEAN_IONIAN = 30.4;

function isInsideMediteranean(lat, lon) {
    return !((lat < MIN_LAT_MEDITERRANEAN || lat > MAX_LAT_MEDITERRANEAN) ||
        (lon < MIN_LON_MEDITERRANEAN || lon > MAX_LON_MEDITERRANEAN))
}

function isInsideAegeanIonian(lat, lon) {
    return !((lat < MIN_LAT_AEGEAN_IONIAN || lat > MAX_LAT_AEGEAN_IONIAN) ||
        (lon < MIN_LON_AEGEAN_IONIAN || lon > MAX_LON_AEGEAN_IONIAN))
}

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

        let lat = e.latlng.lat;
        let lon = e.latlng.lng;
        if (!isInsideMediteranean(lat, lon))
            alert("Point outside of Mediterranean sea. Please select another point");
        else {
            if (isInsideAegeanIonian(lat,lon)) {
                $("#sel1").val("202")
                $("#sel2").val("001")
            }
            else {
                $("#sel1").val("201")
                $("#sel2").val("002")
            }
            if (point2_form.is(":hidden")) {
                $('#lat').val(lat);
                $('#lon').val(lon);
            }
            else if (point3_form.is(":hidden")) {
                $('#lat2').val(lat);
                $('#lon2').val(lon);
            }
            else {
                $('#lat3').val(lat);
                $('#lon3').val(lon);
            }
        }
        if (user_marker != undefined) {
            map.removeLayer(user_marker);
        }


        user_marker = L.marker([lat, lon],  {draggable:true}).bindPopup("AS4254").addTo(map);
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
        if (isInsideMediteranean(lat, lng)  &&
            ((lat2 === "" || lng2 === "") || isInsideMediteranean(lat2, lng2)) &&
            ((lat3 === "" || lng3 === "") || isInsideMediteranean(lat3, lng3))) {
            lat4 = lng4 = lat5 = lng5 = ''
            start_date2 = $("#startdatepicker2 input").datepicker({dateFormat: "yy-mm-dd"}).val();
            start_date3 = $("#startdatepicker3 input").datepicker({dateFormat: "yy-mm-dd"}).val();
            start_date4 = start_date5 = ''
            duration2 = $("#vis_duration2").val();
            duration3 = $("#vis_duration3").val();
            duration4 = duration5 = '';
            var oil_volume2 = $("#oil_volume2").val();
            var oil_volume3 = $("#oil_volume3").val();
            var oil_volume4 = oil_volume5 = '';

            var start_date = $("#startdatepicker input").datepicker({dateFormat: "yy-mm-dd"}).val();
            var enddate = $("#enddatepicker input").datepicker({dateFormat: "yy-mm-dd"}).val();

            var wave_dataset = $("#sel1").val();
            var hd_dataset = $("#sel2").val();

            var url = "http://localhost:8000/oilspill/process/?csrfmiddlewaretoken=LlLKJ7OlQGdAUeWOeOT52n" +
                "Y6Z5dlBNu9OqDB0X2nu6egRBPUrbY5PiTWWUxTF1tg" +
                "&latitude1=" + lat +
                "&longitude1=" + lng +
                "&start_date1=" + start_date +
                "&duration1=" + duration +
                "&latitude2=" + lat2 +
                "&longitude2=" + lng2 +
                "&start_date2=" + start_date2 +
                "&duration2=" + duration2 +
                "&latitude3=" + lat3 +
                "&longitude3=" + lng3 +
                "&start_date3=" + start_date3 +
                "&duration3=" + duration3 +
                "&latitude4=" + lat4 +
                "&longitude4=" + lng4 +
                "&start_date4=" + start_date4 +
                "&duration4=" + duration4 +
                "&latitude5=" + lat5 +
                "&longitude5=" + lng5 +
                "&start_date5=" + start_date5 +
                "&duration5=" + duration5 +
                "&end_date=" + enddate +
                "&oil_volume1=" + oil_volume +
                "&oil_volume2=" + oil_volume2 +
                "&oil_volume3=" + oil_volume3 +
                "&oil_volume4=" + oil_volume4 +
                "&oil_volume5=" + oil_volume5 +
                "&oil_density=" + oil_density +
                "&simulation_length=" + simulation_length +
                "&time_interval=" + time_interval +
                "&wave_model=" + wave_dataset +
                "&hd_model=" + hd_dataset;

            console.log(url);
            window.location.replace(url);
        }
        else {
            alert("Please select points inside Mediterranean sea")
        }
    });

});