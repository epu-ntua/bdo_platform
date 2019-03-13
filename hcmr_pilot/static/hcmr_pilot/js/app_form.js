

var single_marker_layer;
var user_marker = {};
var mode=null;
var first_user_marker = {};
var first_marker_layer;
var second_user_marker = {};
var second_marker_layer;
var third_user_marker ={};
var third_marker_layer;
var fourth_user_marker ={};
var fourth_marker_layer;
var fifth_user_marker ={};
var fifth_marker_layer;

var areaSelect;
var area_bounds;
var bounds = [-90,-180,90,180];
var lock = 0;

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

function create_new_area_select(area_select_bounds){
    $(".leaflet-interactive").remove();
    areaSelect = L.rectangle(area_select_bounds);
    map.addLayer(areaSelect);
    areaSelect.editing.enable();
    area_bounds = areaSelect.getBounds();
    areaSelect.on("edit", function() {
        area_bounds = this.getBounds();
    });
    // map.fitBounds(area_select_bounds);
    bounds = [area_select_bounds[0][0],area_select_bounds[0][1],area_select_bounds[1][0],area_select_bounds[1][1]];
    $('#lat_min').val(bounds[0]);
    $('#lat_max').val(bounds[2]);
    $('#lon_min').val(bounds[1]);
    $('#lon_max').val(bounds[3]);

}

$(document).ready(function() {
    // var startdate = new Date();
    // var enddate = new Date();
    var scenario = $('.scenario').data('id');
    $('.ui.dropdown').dropdown();
    var startpick = $('#startdatepicker').datetimepicker({
        autoclose: true,
        pickerPosition: 'top-left',

    });

    if(scenario === 2){

        create_new_area_select([[29.2575,-15.2578],[49.479,42.0898]]);

        var startpick2 = $('#startdatepicker2').datetimepicker({
            autoclose: true,
            pickerPosition: 'top-left',

        });

        var startpick3 = $('#startdatepicker3').datetimepicker({
            autoclose: true,
            pickerPosition: 'top-left',

        });

        second_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Second Marker");
        third_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Third Marker");
        fourth_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Fourth Marker");
        fifth_user_marker = L.marker([38.06, 25.36],  {draggable:true}).bindPopup("Fifth Marker");

        second_marker_layer = L.layerGroup(second_user_marker);
        third_marker_layer = L.layerGroup(third_user_marker);
        fourth_marker_layer = L.layerGroup(fourth_user_marker);
        fifth_marker_layer = L.layerGroup(fifth_user_marker);

        map.addLayer(second_marker_layer);
        map.addLayer(third_marker_layer);
        map.addLayer(fourth_marker_layer);
        map.addLayer(fifth_marker_layer);
    }



    if (scenario === 1) {

        first_user_marker = L.marker([38.06, 25.36], {draggable: true}).bindPopup("First Marker").addTo(map);

        first_marker_layer = L.layerGroup(first_user_marker);

        map.addLayer(first_marker_layer);


        $('#lat').val(38.06);
        $('#lon').val(25.36);

        var endpick = $('#enddatepicker').datetimepicker({
            autoclose: true,
            pickerPosition: 'top-left',

        });


        first_user_marker.on('dragend', function (e) {

            $('#lat').val(e.target._latlng.lat);
            $('#lon').val(e.target._latlng.lng);
            // let lat = e.latlng.lat;
            // let lon = e.latlng.lng;
            if (isInsideAegeanIonian(e.target._latlng.lat, e.target._latlng.lng)) {
                $("#sel1").val("202");
                $("#sel2").val("001");
            } else if (isInsideMediteranean(e.target._latlng.lat, e.target._latlng.lng)) {
                $("#sel1").val("201")
                $("#sel2").val("002")
            } else {
                alert("Point outside of Mediterranean sea. Please select another point");
                var latlng = L.latLng(38.06, 25.36);
                first_user_marker.setLatLng(latlng).update(first_user_marker);
                $('#lat').val(38.06);
                $('#lon').val(25.36);

            }
        });

    }

    $('#lock_area').on('click', function(e){

        lock = 1;

        areaSelect.editing.disable();

        $('.spatial-selection').hide();
        $('.points-container').show();
        $('.service-buttons').show();
         // $('.lock-button').hide();
        area_bounds = areaSelect.getBounds();
        var swlat = Math.round(area_bounds.getSouthWest().lat * 10000) / 10000;
        var swlon = Math.round(area_bounds.getSouthWest().lng * 10000) / 10000;
        var nelat = Math.round(area_bounds.getNorthEast().lat * 10000) / 10000;
        var nelon = Math.round(area_bounds.getNorthEast().lng * 10000) / 10000;
        bounds = [swlat,swlon,nelat,nelon];
        $('#lat_min').val(bounds[0]);
        $('#lat_max').val(bounds[2]);
        $('#lon_min').val(bounds[1]);
        $('#lon_max').val(bounds[3]);
        first_user_marker = L.marker([(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2], {draggable: true}).bindPopup("First Marker").addTo(map);
        first_marker_layer = L.layerGroup(first_user_marker);
        map.addLayer(first_marker_layer);
        $('#lat').val((bounds[0] + bounds[2]) / 2);
        $('#lon').val((bounds[1] + bounds[3]) / 2);
        map.setView([(bounds[0] + bounds[2]) / 2,(bounds[1] + bounds[3]) / 2], 10);

    });

    $('#unlock-area').on('click', function(e){
        areaSelect.editing.enable();
        lock = 0;
        if (first_user_marker != undefined) {
            map.removeLayer(first_user_marker);
        }
        if (second_user_marker != undefined) {
            map.removeLayer(second_user_marker);
        }
        if (third_user_marker != undefined) {
            map.removeLayer(third_user_marker);
        }
        if (fourth_user_marker != undefined) {
            map.removeLayer(fourth_user_marker);
        }
        if (fifth_user_marker != undefined) {
            map.removeLayer(fifth_user_marker);
        }
        $("#point2_form").removeClass("in");
        $("#point2_form").removeClass("active");
        $("#point3_form").removeClass("in");
        $("#point3_form").removeClass("active");
        $("#point4_form").removeClass("in");
        $("#point4_form").removeClass("active");
        $("#point5_form").removeClass("in");
        $("#point5_form").removeClass("active");
        $('.nav-item').children('a[href="#point2_form"]').removeAttr('data-toggle');
        $('.nav-item').children('a[href="#point2_form"]').parent().removeClass('active');
        $('.nav-item').children('a[href="#point2_form"]').parent().addClass('disabled');
        $('.nav-item').children('a[href="#point3_form"]').removeAttr('data-toggle');
        $('.nav-item').children('a[href="#point3_form"]').parent().removeClass('active');
        $('.nav-item').children('a[href="#point3_form"]').parent().addClass('disabled');
        $('.nav-item').children('a[href="#point4_form"]').removeAttr('data-toggle');
        $('.nav-item').children('a[href="#point4_form"]').parent().removeClass('active');
        $('.nav-item').children('a[href="#point4_form"]').parent().addClass('disabled');
        $('.nav-item').children('a[href="#point5_form"]').removeAttr('data-toggle');
        $('.nav-item').children('a[href="#point5_form"]').parent().removeClass('active');
        $('.nav-item').children('a[href="#point5_form"]').parent().addClass('disabled');
        $("#point1_form").addClass("in");
        $("#point1_form").addClass("active");
        $('.nav-item').children('a[href="#point1_form"]').parent().addClass('active');
        $('.spatial-selection').show();
        $('.points-container').hide();
        $('.service-buttons').hide();
    });



    map.on('click', function (e) {
        if(lock === 1) {
            if (first_user_marker != undefined) {
                map.removeLayer(first_user_marker);
            }

            first_user_marker = L.marker([e.latlng.lat, e.latlng.lng], {draggable: true}).bindPopup("First Marker").addTo(map);
            first_marker_layer = L.layerGroup(first_user_marker);
            map.addLayer(first_marker_layer);
            let lat = e.latlng.lat;
            let lon = e.latlng.lng;
            if (isInsideAegeanIonian(lat, lon)) {
                $("#sel1").val("202");
                $("#sel2").val("001");
            } else if (isInsideMediteranean(lat, lon)) {
                $("#sel1").val("201")
                $("#sel2").val("002")
            } else {
                alert("Point outside of Mediterranean sea. Please select another point");
                if (first_user_marker != undefined) {
                    map.removeLayer(first_user_marker);
                }
                first_user_marker = L.marker([38.06, 25.36], {draggable: true}).bindPopup("First Marker").addTo(map);

                first_marker_layer = L.layerGroup(first_user_marker);

                map.addLayer(first_marker_layer);
                $('#lat').val(38.06);
                $('#lon').val(25.36);

            }

            $('#lat').val(e.latlng.lat);
            $('#lon').val(e.latlng.lng);
            first_user_marker.on('dragend', function (e) {

                $('#lat').val(e.target._latlng.lat);
                $('#lon').val(e.target._latlng.lng);
            });

        }
    });




    // map.on('click', function(e){
    //
    //     point2_form = $("#point2_form");
    //     point3_form = $("#point3_form");
    //
    //     let lat = e.latlng.lat;
    //     let lon = e.latlng.lng;
    //     if (!isInsideMediteranean(lat, lon))
    //         alert("Point outside of Mediterranean sea. Please select another point");
    //     else {
    //         if (isInsideAegeanIonian(lat,lon)) {
    //             $("#sel1").val("202")
    //             $("#sel2").val("001")
    //         }
    //         else {
    //             $("#sel1").val("201")
    //             $("#sel2").val("002")
    //         }
    //         if (point2_form.is(":hidden")) {
    //             $('#lat').val(lat);
    //             $('#lon').val(lon);
    //         }
    //         else if (point3_form.is(":hidden")) {
    //             $('#lat2').val(lat);
    //             $('#lon2').val(lon);
    //         }
    //         else {
    //             $('#lat3').val(lat);
    //             $('#lon3').val(lon);
    //         }
    //     }
    //     if (user_marker != undefined) {
    //         map.removeLayer(user_marker);
    //     }
    //
    //
    //     user_marker = L.marker([lat, lon],  {draggable:true}).bindPopup("AS4254").addTo(map);
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
    // $("#new_point").click(function(){
    //     point2_form = $("#point2_form");
    //     if (point2_form.is(":hidden"))
    //       point2_form.show();
    //     else
    //         $("#point3_form").show();
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
        area_bounds = areaSelect.getBounds();
        var swlat = Math.round(area_bounds.getSouthWest().lat * 10000) / 10000;
        var swlon = Math.round(area_bounds.getSouthWest().lng * 10000) / 10000;
        var nelat = Math.round(area_bounds.getNorthEast().lat * 10000) / 10000;
        var nelon = Math.round(area_bounds.getNorthEast().lng * 10000) / 10000;
        // var x_mov = (nelat - swlat) / swlat;
        // var y_mov = (nelon - swlon) / swlon;
        bounds = [swlat,swlon,nelat,nelon];

        if ( tabid2 === "#point2_form"){

            if (second_user_marker != undefined) {
                map.removeLayer(second_user_marker);
            }
            var redIcon = new L.Icon({
                iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'
            });
            second_user_marker = L.marker([((bounds[0] + bounds[2] ) / 2) - 0.01, ((bounds[1] + bounds[3] ) / 2) - 0.01], {draggable:true}, {icon: redIcon}).bindPopup("Second Marker").addTo(map);
            second_user_marker.setIcon(redIcon);
            second_marker_layer = L.layerGroup(second_user_marker);
            map.addLayer(second_marker_layer);
            second_user_marker.on('dragend', function (e) {

                $('#lat2').val(e.target._latlng.lat);
                $('#lon2').val(e.target._latlng.lng);
            });
            $('#lat2').val(((bounds[0] + bounds[2] ) / 2) - 0.01);
            $('#lon2').val(((bounds[1] + bounds[3] ) / 2) - 0.01);
        }
        else if(tabid2 === "#point3_form"){
            if (third_user_marker != undefined) {
                map.removeLayer(third_user_marker);
            }
            var greenIcon = new L.Icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png'
            });
            third_user_marker = L.marker([((bounds[0] + bounds[2]) / 2) - 0.01, ((bounds[1] + bounds[3] ) / 2) + 0.01 ], {draggable:true}, {icon: greenIcon}).bindPopup("Third Marker").addTo(map);
            third_user_marker.setIcon(greenIcon);
            third_marker_layer = L.layerGroup(third_user_marker);
            map.addLayer(third_marker_layer);

            third_user_marker.on('dragend', function (e) {
                $('#lat3').val(e.target._latlng.lat);
                $('#lon3').val(e.target._latlng.lng);
            });

            $('#lat2').val(((bounds[0] + bounds[2] ) / 2) - 0.01);
            $('#lon2').val(((bounds[1] + bounds[3] ) / 2) + 0.01);

        }
        else if (tabid2 === "#point4_form"){
            if (fourth_user_marker != undefined) {
                map.removeLayer(fourth_user_marker);
            }
            var orangeIcon = new L.Icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png'
            });
            fourth_user_marker = L.marker([((bounds[0] + bounds[2] ) / 2) + 0.01, ((bounds[1] + bounds[3]) / 2) - 0.01], {draggable:true}, {icon: greenIcon}).bindPopup("Fourth Marker").addTo(map);
            fourth_user_marker.setIcon(orangeIcon);
            fourth_marker_layer = L.layerGroup(fourth_user_marker);
            map.addLayer(fourth_marker_layer);

            fourth_user_marker.on('dragend', function (e) {
                $('#lat4').val(e.target._latlng.lat);
                $('#lon4').val(e.target._latlng.lng);
            });

            $('#lat2').val(((bounds[0] + bounds[2] ) / 2) + 0.01);
            $('#lon2').val(((bounds[1] + bounds[3] ) / 2) - 0.01);
        }
        else if (tabid2 === "#point5_form"){
            if (fifth_user_marker != undefined) {
                map.removeLayer(fifth_user_marker);
            }
            var blackIcon = new L.Icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-black.png'
            });
            fifth_user_marker = L.marker([((bounds[0] + bounds[2] ) / 2) + 0.01, ((bounds[1] + bounds[3] ) / 2) + 0.01], {draggable:true}, {icon: greenIcon}).bindPopup("Fourth Marker").addTo(map);
            fifth_user_marker.setIcon(blackIcon);
            fifth_marker_layer = L.layerGroup(fifth_user_marker);
            map.addLayer(fifth_marker_layer);

            fifth_user_marker.on('dragend', function (e) {
                $('#lat5').val(e.target._latlng.lat);
                $('#lon5').val(e.target._latlng.lng);
            });

            $('#lat2').val(((bounds[0] + bounds[2] ) / 2) + 0.01);
            $('#lon2').val(((bounds[1] + bounds[3] ) / 2) + 0.01);
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

    $('#remove_point4').click(function () {
        $('#lat4').val("");
        $('#lon4').val("");
        if (fourth_user_marker != undefined) {
            map.removeLayer(fourth_user_marker);
        }
        $("#point4_form").removeClass("in");
        $("#point4_form").removeClass("active");
        $("#point1_form").addClass("in");
        $("#point1_form").addClass("active");
        $('.nav-item').children('a[href="#point4_form"]').removeAttr('data-toggle');
        $('.nav-item').children('a[href="#point4_form"]').parent().removeClass('active');
        $('.nav-item').children('a[href="#point4_form"]').parent().addClass('disabled');
        $('.nav-item').children('a[href="#point1_form"]').parent().addClass('active');
    });

    $('#remove_point5').click(function () {
        $('#lat5').val("");
        $('#lon5').val("");
        if (fifth_user_marker != undefined) {
            map.removeLayer(fifth_user_marker);
        }
        $("#point5_form").removeClass("in");
        $("#point5_form").removeClass("active");
        $("#point1_form").addClass("in");
        $("#point1_form").addClass("active");
        $('.nav-item').children('a[href="#point5_form"]').removeAttr('data-toggle');
        $('.nav-item').children('a[href="#point5_form"]').parent().removeClass('active');
        $('.nav-item').children('a[href="#point5_form"]').parent().addClass('disabled');
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