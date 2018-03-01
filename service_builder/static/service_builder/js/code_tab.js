$(document).ready(function(){
    $("#load_query_popbtn").popover({
        html: true,
        animation:true,
        trigger: 'manual',
        content: function() {
            return $('#load-query-select-container').html();
        }
    }).click(function(e) {
        $(this).popover('toggle');

        $('#load-query-select').empty();
        $('#load-query-select').append('<option disabled selected>-- select one of the queries to load --</option>');

        $('#selected-queries-table tbody tr').each(function( index ) {
            var query_id = $( this ).children().eq(0).text();
            var query_display_name = $( this ).children().eq(1).text();
            var query_name = $( this ).children().eq(2).text();
            $('#load-query-select').append('<option  data-query-id="'+query_id+'" data-display_name="'+query_display_name+'" title="' + query_display_name + '-' + query_name + '"> ' + query_display_name + '-' + query_name + ' </option>');
        });
        $('.popover-content #load-query-select').select2();


        var load_query_id;
        var selected = false;
        $('.popover-content #load-query-select').on('change', function() {
            selected = true;
            load_query_id = $(this).children(":selected").attr("data-query-id");
        });




        $('.popover-content #load_query_btn').click(function (e) {
            // alert(load_query_id);

            selected = false;
            $('#load_query_popbtn').popover("hide");
        })
    });
});
