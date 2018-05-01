// <script type="text/javascript">
// Get form fields of all the service arguments
$(document).ready(function () {
  $.ajax({
        url: '/service_builder/load_service_args_form_fields/',
        data: {
            service_id: get_service_id()
        },
        type: 'GET',
        success: function(form_fields){
            $("#service_args_container").html(form_fields);
        }
    });
});





// Submit the service arguments
$("#submitServiceConfig").click(function (element) {
  $.ajax({
        url: '/service_builder/service/'+get_service_id()+'/execute/',
        data: $('#service_args_container').serialize(),
        type: 'GET',
        beforeSend: function(){
            $("#service_result_container").show();
            $(".loadingDiv").css( "display", "block" );
        },
        success: function(result){
            $("#service_result_container").html( result );
            // $("iframe").each(function () {
            //     var src = $( this ).attr('data-src');
            //     jQuery.each(result['query_mapping'], function(query, temp_query) {
            //       src = src.replace(new RegExp("query="+query+"&"), "query="+temp_query+"&");
            //       src = src.replace(new RegExp("query="+query+"$"), "query="+temp_query);
            //     });
            //     $( this ).attr({'src': src});
            // });
            $(".loadingDiv").css( "display", "none" );
            $(".loadingFrame").css( "display", "block" );
            $(".viz_container iframe").on( "load", function(){
                $(this).siblings(".loadingFrame").css( "display", "none" )
            });

        },
        error: function () {
            $(".loadingDiv").css( "display", "none" );
            $("#service_result_container").hide();
            alert('An error occured');
        }
    });
});
    // </script>