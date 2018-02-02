$(document).ready(function() {
//========================================================================
//              Data Configuration
// ========================================================================
    var lat,lon,ship,date,speed,colour;
    var marray = [];
    var course = [];
    var paused = false;
    data = JSON.parse(data);
    $.each(data,function(index,value){
        $.each(data[index],function(key, value){
            switch(key) {
                case 'ship':
                    ship = value;
                    break;
                case 'lat':
                    lat = value;
                    break;
                case 'lon':
                    lon = value;
                    break;
                case 'date':
                    date = value;
                    break;
                case 'speed':
                    speed = value;
                    break;
                case 'colour':
                    colour = value;
                    break;
            }
        });
        marray.push([ship,lat,lon,date,speed,colour]);
        course.push([lat,lon]);
    });
//========================================================================
//              Map Configuration
// ========================================================================
    //var map = $('.leaflet-container-default');
    map = window[name];
    //map = window[map.attr('id')];
    L.easyButton('fa-play', function(){
        play();
    }).addTo(map);

    L.easyButton('fa-pause', function(){
        pause();
    }).addTo(map);

    var url = 'https://cdn4.iconfinder.com/data/icons/geo-points-1/154/geo-location-gps-sea-location-boat-ship-512.png';
    var icon = L.icon({
        //iconUrl: url,
        iconUrl: 'http://localhost:8000/static/img/shipmarker.png',
        iconSize: [40, 40],
        iconAnchor: [20, 20]
    });

    var ar = new Array(course.length).fill(2000);

    var movinglayer = new L.layerGroup();
    var courselayer = new L.layerGroup();
        var overlayMaps = {
        "Course": courselayer,
        "Moving Marker": movinglayer
    };
    map.fitBounds(course);
    map.on('baselayerchange', onLayerChange);
//========================================================================
//              Moving Marker
// ========================================================================
    var mar = new L.Marker.MovingMarker(course, ar, {icon: icon, autostart:false});
    var popup = false;
    mar.on('click', function () {
        if(mar.isRunning()) {
            mar.pause();
        }
        var location = mar.getLatLng();
        var i,text;
        i = mar.getLine();

        if(!mar.isPopupOpen()){
            popup = false;
            mar.unbindPopup();
        }
        if(!location.equals(course[i])){
            if(location.equals(course[i-1])){
                i -= 1;
            }
            else{
                i *= -1;
            }
        }
        if(i < 0){
            i *= -1;
            text = "<b> Ship: </b>" + marray[i][0] + "<br><b> Between: </b>" + marray[i-1][3] + "<b> And: </b>" + marray[i][3] + "<br><b> Speed From: </b>" + marray[i-1][4] + "<b> To: </b>" + marray[i][4];
            text += "<br><b>Location: </b>[" + location.lat + "," + location.lng + "]";
        }
        else{
            text = "<b>Ship: </b>" + marray[i][0] + "<br><b> On: </b>" + marray[i][3] + "<br><b> Speed: </b>" + marray[i][4];
            text += "<br><b>Location: </b>[" + location.lat + "," + location.lng + "]";
        }

        mar.bindPopup(text);
        if(!popup){
            popup = true;
            mar.openPopup();
        }
        else{
            popup = false;
            mar.closePopup();
            mar.unbindPopup();
        }
    });

    mar.addTo(movinglayer);

//========================================================================
//              FeatureGroup - CourseLayer
// ========================================================================
    var newroute = [];
    var s,t,u,v;
    var linecolor = 'green';
    for(var i=0;i<course.length-1;i++){
        s = new L.marker(course[i],{icon:icon}).bindPopup("<b> Ship: </b>" + marray[i][0] + "<br><b> On: </b>" + marray[i][3] + "<br><b> Speed: </b>" + marray[i][4]);
        if(marray[i+1][5]=='red'){
            linecolor = 'red';
        }
        t = new L.polyline([course[i], course[i+1]],{color:linecolor, opacity:0.4, weight:5, lineCap: 'round'});
        //v = new L.polyline([course[i], course[i+1]],{color:linecolor});
        u = new L.polylineDecorator([course[i], course[i+1]],{
            patterns: [
                {offset: '0', repeat: 30, symbol: L.Symbol.arrowHead({pixelSize: 10, polygon: false, pathOptions: {color: linecolor, opacity: 0.5, weight: 5}})}
            ]
        });
        //v.addTo(movinglayer);
        u.addTo(movinglayer);
        newroute.push(s,t);
        linecolor = 'green';
    }
    s = new L.marker(course[course.length-1],{icon:icon}).bindPopup("<b> Ship: </b>" + marray[i][0] + "<br><b> On: </b>" + marray[i][3] + "<br><b> Speed: </b>" + marray[i][4]);
    newroute.push(s);

    var tour = new L.featureGroup(newroute,{snakingSpeed: 800});
    tour.addTo(courselayer);


    courselayer.addTo(map);
    L.control.layers(overlayMaps,null,{collapsed:false}).addTo(map);
//========================================================================
//              Animate Function
// ========================================================================
    function play(){
        if(mar.isPopupOpen()){
            mar.closePopup();
        }
        mar.start();

        if(paused){
            tour.snakecontinue();
            paused = false;
        }
        else{
            tour.snakeIn();
        }
        //tour.on('snakestart snake snakeend', function (ev) {
        //    console.log(ev.type);
        //});
    }

    function pause(){
        tour.snakepause();
        mar.pause();
        paused = true;
    }


    function onLayerChange(e){
        if( e.name == 'Moving Marker' ){
            tour.snakepause();
            paused = true;
        }
        else if( e.name == 'Course' ){
            tour.snakecontinue();
            paused = false;
        }
    }
//========================================================================

});
