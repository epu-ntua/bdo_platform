$(document).ready(function(){

    var min_year = parseInt(document.getElementById('min_year').innerHTML);
    var max_year = document.getElementById('max_year').innerHTML;


    $('#id_tiles').on('change', function(e){
        var selected = $(this).find(":selected").text();
        var url;
        switch (selected) {
            case 'Marker Clusters':
               url = 'https://blog.dominodatalab.com/wp-content/uploads/2016/05/1000recordsmap.png';
               break;
            case 'Heatmap':
                url = 'http://blog.cloudera.com/wp-content/uploads/2016/07/datastory-f2.png';
                break;
        }
        document.getElementById('map_preview').setAttribute("src",url);
    });


    $('#rangeslider').slider({
        range: true,
        min: 2000,
        max: 2017,
        values: [ min_year, max_year],
        slide: function( event, ui ) {
          $('#rangeval').html(ui.values[0]+" - "+ui.values[1]);
          document.getElementById('min_year').innerHTML = ui.values[0] + " - ";
          document.getElementById('max_year').innerHTML = ui.values[1];
          document.getElementById('id_min_year').value = ui.values[0];
          document.getElementById('id_max_year').value = ui.values[1];
        }
    });


    $('#submit').on('click', function(e){
        document.getElementById('loading').setAttribute("style","position: fixed; left: 50%; top: 50%; visibility: visible;");
    });

});