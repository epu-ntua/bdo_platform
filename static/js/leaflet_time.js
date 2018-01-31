$(document).ready(function() {
    map = window[name];

    var lindex = 0, mindex = -1;
    var lat, lon;

    data = JSON.parse(data);
//========================================================================
//              Setting Map Boundaries
// =======================================================================
    var bounds = [data.length];
    for(var j=0; j<data.length; j++){
        var point = (data[j].geometry['coordinates'][0]).toString();
        lat = point.split(',')[1];
        lon = point.split(',')[0];
        bounds[j]=[lat,lon];
    }
    if(data.length>0){
        if(data.length>1){
            map.fitBounds(bounds);
        }
        else{
            map.setView(bounds[0],13);
        }
    }
//========================================================================
//              Setting Map Boundaries
// =======================================================================
//========================================================================
//              Setting Markers And Playback
// =======================================================================
    var icon = L.icon({
        iconUrl: 'http://localhost:8000/static/img/shipmarker.png',
        iconSize: [40, 40],
        iconAnchor: [20, 20]
    });

    var playbackOptions = {
        orientIcons:false,
        popups:true,
        //fadeMarkersWhenStale:true,
        //tickLen: 1000,

        layer: {
            pointToLayer : function(featureData, latlng) {
                var result;
                result = { "color" : featureData.properties['colour'][lindex] };
                result.radius = 5;
                lindex++;

                return new L.CircleMarker(latlng, result);
            }
        },

        marker: function(featureData){
            return{
                icon: icon,
                getPopup: function (featureData) {
                    mindex++;
                    return "Ship: " + featureData.properties['ship'] + "<br>On: " + featureData.properties['date'][mindex] + "<br>Speed: " + featureData.properties['speed'][mindex];
                }
            };
        }
    };

    var playback = new L.Playback(map, data, null, playbackOptions);

    var control = new L.Playback.Control(playback);
    control.addTo(map);
//========================================================================
//              Setting Markers And Playback
// =======================================================================
});