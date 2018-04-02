    $("#argsModalBtn").click(function (element) {
        $.ajax({
            url: '/service_builder/load_service_args_form_fields/',
            data: { service_id: get_service_id() },
            type: 'GET',
            success: function(form_fields){
                $("#service_args_container").html(form_fields);
            }
        });
    });

    $(".viz_container iframe").on( "load", function(){
        $(this).siblings(".loadImg").css( "display", "none" )
    });

    $("#submitServiceConfig").click(function (element) {
        $.ajax({
            url: '/service_builder/submit_service_args/',
            data: { service_id: get_service_id(), arguments: $('#service_args_container').serialize() },
            type: 'GET',
            success: function(result){
                $("iframe").each(function () {
                    /* var src_a = $( this ).attr('src-a'); jQuery.each(result['query_mapping'], function(query, temp_query) { src_a = src_a.replace("query="+query, "query="+temp_query); }); $( this ).attr({'src': src_a}); $( this ).show(); */
                });
            }
        });
    });
