$(document).ready(function(){
    var csrftoken = Cookies.get('csrftoken');
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    var notebook_id = $('#notebook_id').val();

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
            if (selected){
                // alert(load_query_id);
                // alert(notebook_id);
                var exposed_args=[];
                $("#selected-arguments-table tbody tr").each(
                    function(index, elem){
                        if($(this).children().eq(0).text()==load_query_id){
                            console.log($(this).text());
                            exposed_args.push({
                                filter_a: $(this).children().eq(2).children().eq(0).text(),
                                filter_op: $(this).children().eq(2).children().eq(1).text(),
                                filter_b: $(this).children().eq(3).children().eq(0).val()
                            });
                        }
                    }
                );
                $.ajax({
                    "type": "POST",
                    "url": "/service_builder/load_query/",
                    "data": {
                        query_id: load_query_id,
                        notebook_id: notebook_id,
                        exposed_args: JSON.stringify(exposed_args)
                    },
                    "success": function(result) {
                        console.log(result);
                    },
                    error: function (jqXHR) {
                        alert('error');
                    }
                });
            }
            selected = false;
            $('#load_query_popbtn').popover("hide");
        })
    });
});
