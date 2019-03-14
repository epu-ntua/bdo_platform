

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

function ckeck_markers_location() {
    area_bounds = areaSelect.getBounds();
    var swlat = Math.round(area_bounds.getSouthWest().lat * 10000) / 10000;
    var swlon = Math.round(area_bounds.getSouthWest().lng * 10000) / 10000;
    var nelat = Math.round(area_bounds.getNorthEast().lat * 10000) / 10000;
    var nelon = Math.round(area_bounds.getNorthEast().lng * 10000) / 10000;
    bounds = [swlat,swlon,nelat,nelon];
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
        lock = 1;
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

    if(scenario === 3){
        lock = 1;
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
        $('#unlock-area').show();
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
        map.setView([(bounds[0] + bounds[2]) / 2,(bounds[1] + bounds[3]) / 2], 9);

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
        $('#unlock-area').hide();
         area_bounds = areaSelect.getBounds();
        var swlat = Math.round(area_bounds.getSouthWest().lat * 10000) / 10000;
        var swlon = Math.round(area_bounds.getSouthWest().lng * 10000) / 10000;
        var nelat = Math.round(area_bounds.getNorthEast().lat * 10000) / 10000;
        var nelon = Math.round(area_bounds.getNorthEast().lng * 10000) / 10000;
        bounds = [swlat,swlon,nelat,nelon];
         map.setView([(bounds[0] + bounds[2]) / 2,(bounds[1] + bounds[3]) / 2], 6);

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



    $(".new_point").click(function(){
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
        var x_mov = 3*(nelat - swlat) / swlat;
        var y_mov = 3*(nelon - swlon) / swlon;
        bounds = [swlat,swlon,nelat,nelon];

        if ( tabid2 === "#point2_form"){

            if (second_user_marker != undefined) {
                map.removeLayer(second_user_marker);
            }
            var startpick = $('#startdatepicker2').datetimepicker({
                autoclose: true,
                pickerPosition: 'top-left',

            });
            var redIcon = new L.Icon({
                iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'
            });
            second_user_marker = L.marker([((bounds[0] + bounds[2] ) / 2) - x_mov, ((bounds[1] + bounds[3] ) / 2) - y_mov], {draggable:true}, {icon: redIcon}).bindPopup("Second Marker").addTo(map);
            second_user_marker.setIcon(redIcon);
            second_marker_layer = L.layerGroup(second_user_marker);
            map.addLayer(second_marker_layer);
            second_user_marker.on('dragend', function (e) {

                $('#lat2').val(e.target._latlng.lat);
                $('#lon2').val(e.target._latlng.lng);
            });
            var lat = ((bounds[0] + bounds[2] ) / 2) - 0.1;
            var lng = ((bounds[1] + bounds[3] ) / 2) - 0.1;
            $('#lat2').val(lat);
            $('#lon2').val(lng);
        }
        else if(tabid2 === "#point3_form"){
            var startpick = $('#startdatepicker3').datetimepicker({
                autoclose: true,
                pickerPosition: 'top-left',

            });
            if (third_user_marker != undefined) {
                map.removeLayer(third_user_marker);
            }
            var greenIcon = new L.Icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png'
            });
            third_user_marker = L.marker([((bounds[0] + bounds[2]) / 2) - x_mov, ((bounds[1] + bounds[3] ) / 2) + y_mov ], {draggable:true}, {icon: greenIcon}).bindPopup("Third Marker").addTo(map);
            third_user_marker.setIcon(greenIcon);
            third_marker_layer = L.layerGroup(third_user_marker);
            map.addLayer(third_marker_layer);

            third_user_marker.on('dragend', function (e) {
                $('#lat3').val(e.target._latlng.lat);
                $('#lon3').val(e.target._latlng.lng);
            });
            var lat = ((bounds[0] + bounds[2] ) / 2) - 0.1;
            var lng = ((bounds[1] + bounds[3] ) / 2) + 0.1;
            $('#lat3').val(lat);
            $('#lon3').val(lng);

        }
        else if (tabid2 === "#point4_form"){
            var startpick = $('#startdatepicker4').datetimepicker({
                autoclose: true,
                pickerPosition: 'top-left',

            });
            if (fourth_user_marker != undefined) {
                map.removeLayer(fourth_user_marker);
            }
            var orangeIcon = new L.Icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png'
            });
            fourth_user_marker = L.marker([((bounds[0] + bounds[2] ) / 2) + x_mov, ((bounds[1] + bounds[3]) / 2) - y_mov], {draggable:true}, {icon: greenIcon}).bindPopup("Fourth Marker").addTo(map);
            fourth_user_marker.setIcon(orangeIcon);
            fourth_marker_layer = L.layerGroup(fourth_user_marker);
            map.addLayer(fourth_marker_layer);

            fourth_user_marker.on('dragend', function (e) {
                $('#lat4').val(e.target._latlng.lat);
                $('#lon4').val(e.target._latlng.lng);
            });
            var lat = ((bounds[0] + bounds[2] ) / 2) + 0.1;
            var lng = ((bounds[1] + bounds[3] ) / 2) - 0.1;
            $('#lat4').val(lat);
            $('#lon4').val(lng);
        }
        else if (tabid2 === "#point5_form"){
            var startpick = $('#startdatepicker5').datetimepicker({
                autoclose: true,
                pickerPosition: 'top-left',

            });
            if (fifth_user_marker != undefined) {
                map.removeLayer(fifth_user_marker);
            }
            var blackIcon = new L.Icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-black.png'
            });
            fifth_user_marker = L.marker([((bounds[0] + bounds[2] ) / 2) + x_mov, ((bounds[1] + bounds[3] ) / 2) + y_mov], {draggable:true}, {icon: greenIcon}).bindPopup("Fourth Marker").addTo(map);
            fifth_user_marker.setIcon(blackIcon);
            fifth_marker_layer = L.layerGroup(fifth_user_marker);
            map.addLayer(fifth_marker_layer);

            fifth_user_marker.on('dragend', function (e) {
                $('#lat5').val(e.target._latlng.lat);
                $('#lon5').val(e.target._latlng.lng);
            });
            var lat = ((bounds[0] + bounds[2] ) / 2) + 0.1;
            var lng = ((bounds[1] + bounds[3] ) / 2) + 0.1;
            $('#lat5').val(lat);
            $('#lon5').val(lng);
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


    var exec_instance = '';
    $("#run-service-btn").click(function () {
        if(parseInt(scenario) === 1)
            $("#execution_btn_OIL_SPILL_SCENARIO_1").click();
        else if(parseInt(scenario) === 2)
            $("#execution_btn_OIL_SPILL_SCENARIO_2").click();
        else if(parseInt(scenario) === 3)
            $("#execution_btn_OIL_SPILL_SCENARIO_3").click();

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

            var natura_layer = $('input[name="natura_checkbox"]:checked').length > 0;
            var ais_layer = $('input[name="ais_checkbox"]:checked').length > 0;

            var url = "/oilspill/" +
                "scenario" + scenario +
                "/process/?" +
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
                "&hd_model=" + hd_dataset +
                "&natura_layer=" + natura_layer +
                "&ais_layer=" + ais_layer;



            console.log(url);
            // window.location.replace(url);
            $("#execution_status").val('starting service');
            $.ajax({
                "type": "GET",
                "url": url,
                "data": {},
                "success": function(result) {
                        console.log(result);
                        exec_instance = result['exec_instance'];
                    },
                    error: function () {
                        alert('error');
                    }
            });

            var execution_status_interval = setInterval(check_execution_status, 3000);

            function check_execution_status() {
                $.ajax({
                    "type": "GET",
                    "url": "/oilspill/"+"scenario"+ scenario+"/status/"+exec_instance+"/",
                    "data": {},
                    "success": function(result) {
                        console.log(result["status"]);
                        $("#execution_status").val(result["status"]);
                        if(result["status"] === "done"){
                            setTimeout(function() {
                                execution_status_stop();
                                window.location.href = "/oilspill/"+"scenario"+ scenario+"/results/"+exec_instance+"/";
                            }, 1000);
                        }
                        else if (result["status"] === "failed") {
                            execution_status_stop();
                            // alert("execution failed");
                        }
                    },
                    error: function () {
                        execution_status_stop();
                        // alert('error');
                    }
                });
            }

            function execution_status_stop() {
                clearInterval(execution_status_interval);
            }

        }
        else {
            alert("Please select points inside Mediterranean sea")
        }
    });


    window.setInterval(function () {
        if($(".modal.in").length > 0) {
            var old_status = $(" .modal.in #modal_status_input").val();
            var new_status = $("#execution_status").val();
            if (old_status !== new_status) {
                console.log(new_status);
                $(".modal.in #modal_status_input").val(new_status);
                $(".modal.in #modal_status_div").fadeOut("2000").html(new_status).fadeIn("2000");
                $(".modal.in .status_counter").each(function (index, elem) {
                    console.log($(elem).data("status"));
                    if ($(elem).attr("data-status") === new_status) {
                        // console.log('found');
                        var new_step_counter = $(elem).attr("data-counter");
                        $(".modal.in .status_counter").each(function (i, e) {
                            if(i <= index){
                                $(e).removeClass('label-default').addClass('label-primary');
                            }
                        });

                        var $total = parseInt($(".modal.in #number_of_steps").val());
                        var $current = parseInt(new_step_counter);
                        var $percent = ($current / $total) * 100;
                        $(".modal.in .progress-bar").css({width: $percent + '%'});
                    }
                });

            }
            if (new_status === "failed"){
                $(".modal.in .progress-bar").css({width: '100%', background: '#db2828'});
                $(".modal.in .status_counter").each(function (index, elem) {
                    $(elem).removeClass('label-default').addClass('label-primary');
                });
                $(".modal.in #modal_dismiss_btn_cancel").hide();
                $(".modal.in #modal_dismiss_btn_close").show();
            }
        }
    }, 1000);

    $('.modal').on('hidden.bs.modal', function () {
        $(" .modal #modal_status_input").val('');
        $("#execution_status").val('');
        $(".modal #modal_dismiss_btn_cancel").show();
        $(".modal #modal_dismiss_btn_close").hide();
        $(".modal .status_counter").each(function (index, elem) {
            $(elem).removeClass('label-default').removeClass('label-primary').addClass('label-default');
        });
        $(".modal .progress-bar").css({width: '0%', background: '#337ab7'});
        $(".modal #modal_status_div").html('');
    });

    // $("#modal_dismiss_btn_cancel").click(function () {
    //     $.ajax({
    //         "type": "GET",
    //         "url": "/wave-energy/"+exec_instance+"/",
    //         "data": {},
    //         "success": function(result) {
    //             console.log('service cancelled');
    //         },
    //         error: function () {
    //             console.log('error cancelling service');
    //         },
    //         complete: function () {
    //             exec_instance = '';
    //         }
    //     });
    // });

});