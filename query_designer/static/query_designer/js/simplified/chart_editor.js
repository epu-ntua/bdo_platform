$('#viz_config select').select2();

function updateVariables(element) {
    $('#addVizModal .variable-select').find('option').remove().end();
    $('#addVizModal .variable-select').append($("<option disabled selected>-- select variable --</option>"));
    var new_query_id = $('#selected_query').val();
    var new_query_doc = {};
    $.ajax({
        url: '/queries/get_query_variables/',
        data: {
            id: new_query_id,
            document: new_query_doc
            },
        type: 'GET',
        success: function(result){
            var variables = result['variables'];
            var dimensions = result['dimensions'];
            $('.variable-select').append($("<option></option>")
                .attr("value", '')
                .text('-- column select --'));
            $.each(variables, function(k, v) {
                $('.variable-select').append($("<option></option>")
                    .attr("value", v)
                    .text(k));
            });

            $.each(dimensions, function(k, v) {
                $('.variable-select').append($("<option></option>")
                    .attr("value", v)
                    .text(k));
            });
        }
    });
}


    $('#addVizModal .select2').on("click", function() {
        $('.popover').popover('hide');
    });

    $('#addVizModal select').on('change', function() {
        $('#addVizModal #viz_config').show();
        var new_query_id = $(this).children(":selected").attr("data-query-id");
        $('#addVizModal #selected_query').val(new_query_id);
        $('.popover').popover('hide');
          // updateVariables(this);
    });



    $(".viz_item").click(function (element) {
      var component_id = $(this).attr('data-viz-id');
      var component_selector = 'li[data-viz-id="'+component_id+'"]';
      $.ajax({
            url: '/dashboards/get_visualization_form_fields',
            data: {
                id: parseInt(component_id),
                order: 1
                },
            type: 'GET',
            success: function(form_fields){
                $("#conf-container").html(form_fields);
                $("#conf-container").append('<button type="button" id="select_conf_ok" class="btn btn-sm btn-success" data-toggle="popover">OK</button>');
                $("#conf-container").append('<button type="button" id="select_conf_cancel" class="btn btn-sm " data-toggle="popover">Cancel</button>');
                $(component_selector).popover({
                    html: true,
                    title: 'Configure visualisation',
                    trigger: 'manual',
                    content: function() {
                        return $('#conf-container').html();
                    }
                });
                updateVariables($('#load-viz-query-select'));
                $('.viz_item').not(component_selector).popover('hide');
                $(component_selector).popover('toggle');
                var popver_id = '#' + $(component_selector).attr('aria-describedby');
                $(popver_id+' #select_conf_ok').click(function(e){
                    $("#viz_container .outputLoadImg").show();
                    submit_conf(component_selector);
                    $(component_selector).popover("hide");
                });
                $(popver_id+' #select_conf_cancel').click(function(e){
                    $(component_selector).popover("hide");
                });
            }
        });
});


var viz_request = "";
function submit_conf(component_selector) {
    viz_request = "/visualizations/";
    var conf_popover_id = '#' + $(component_selector).attr('aria-describedby');
    viz_request += $('#action').val();

    var submitted_args = $(conf_popover_id).find('.popover-content').clone();
    var selects = $(conf_popover_id).find('.popover-content').find("select");
    $(selects).each(function(i) {
        var select = this;
        $(submitted_args).find("select").eq(i).val($(select).val());
    });
    $('#config-viz-form').empty();
    $('#config-viz-form').append(submitted_args);


    var myData = $("#config-viz-form").serialize();
    viz_request += '?';
    viz_request += myData;

    viz_request += '&query=' + $('#selected_query').val();

    show_viz(viz_request);
}

function show_viz(viz_request) {
    var iframe = $('<iframe id="viz-iframe" ' +
        'src="'+viz_request+'" frameborder="0" allowfullscreen="" onload="hide_gif();"'+
        '></iframe>');
    $("#viz_container iframe").remove();
    $("#viz_container").append(iframe);
    // $("#viz_container").html('<iframe id="viz-iframe" ' +
    //     'src="'+viz_request+'" frameborder="0" allowfullscreen="" '+
    //     '></iframe>');
}

function hide_gif(){
    $(".outputLoadImg").css( "display", "none" );
};


// $("#toggleviz_group_container_btn").click(function () {
//     if($('#viz_group_container').is(":visible")){
//         $('#viz_group_container').collapse("hide");
//         $('#viz_container').removeClass('col-sm-10').addClass('col-sm-12');
//     }
//     else{
//         $('#viz_group_container').collapse("show");
//         $('#viz_container').removeClass('col-sm-12').addClass('col-sm-10');
//     }
// });