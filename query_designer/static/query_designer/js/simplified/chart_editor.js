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

                $(component_selector).popover({
                    html: true,
                    title: 'Configure visualisation',
                    trigger: 'manual',
                    content: function() {
                        return $('#conf-container').html();
                    }
                });
                updateVariables($('#load-viz-query-select'));
                $(component_selector).popover('toggle');
                var popver_id = '#' + $(component_selector).attr('aria-describedby');
                $(popver_id+' #select_conf_ok').click(function(e){
                    submit_conf(component_selector);
                    $(component_selector).popover("hide");
                });
            }
        });
});


var viz_request = "";
function submit_conf(component_selector) {
    viz_request = "http://localhost:8000/visualizations/";
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
    $("#viz_container").html('<iframe id="viz-iframe" ' +
        'src="'+viz_request+'" frameborder="0" allowfullscreen="" '+
        '></iframe>');
}