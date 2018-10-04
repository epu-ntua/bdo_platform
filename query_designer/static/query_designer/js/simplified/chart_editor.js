var query_id = $('#query-variables-select-container div').attr("id");

function updateVariables() {
    $('#myModal .variable-select').find('option').remove();
    var content = $('#query-variables-select-container #' + String(query_id)).html();
    $('#myModal .variable-select ').html(content);
}

$(".viz_item").click(function () {
    var component_id = $(this).attr('data-viz-id');
    var component_type = $(this).attr('data-viz-type');
    var component_selector = 'li[data-viz-id="' + component_id + '"]';


    $(component_selector).popover({
        html: true,
        title: 'Configure visualisation',
        trigger: 'manual',
        content: function () {
            return $('.all_viz_forms  #viz_' + String(component_id)).clone();
        }
    });
    updateVariables();


    $(component_selector).popover('show');
    $('div.popover-content .variable-select').each(function (i, e){$("#" + $(e).attr("id")).select2({placeholder:"Select Variable(s)", width: 'element'})});
    $('div.popover-content select').not(".variable-select").each(function (i, e){$("#" + $(e).attr("id")).select2({placeholder:"Select a value", width: 'element'})});

    var popver_id = '#' + $(component_selector).attr('aria-describedby');
    $(popver_id + ' #select_conf_ok').click(function () {
        $("#viz_config .list-group").children().each(function () {
            $(this).find("#selected_viz_span").hide();
        });

        $(component_selector).find("#selected_viz_span").show();
        submit_conf(component_selector, component_type);
        $(component_selector).popover("hide");
    });
    $(popver_id + ' #select_conf_cancel').click(function () {
        $(component_selector).popover("hide");
    });
});


function submit_conf(component_selector, component_type) {
    var conf_popover_id = '#' + $(component_selector).attr('aria-describedby');
    var submitted_args = $(conf_popover_id).find('.popover-content').clone();
    var selects = $(conf_popover_id).find('.popover-content').find("select");
    $(selects).each(function (i) {
        var select = this;
        $(submitted_args).find("select").eq(i).val($(select).val());
        $('#config-viz-form').append(select);
    });
    $('#config-viz-form').empty();
    $('#config-viz-form').append(submitted_args);

    if (component_type !== 'map') {
        var viz_request = "/visualizations/" + $('#myModal').find('.modal-body').find('#action').val();
        var chartData = $("#config-viz-form").serialize();
        viz_request += '?' + chartData + '&query=' + query_id;
        show_viz(viz_request);
    }
    else {
        var json = [];
        var mapChartData = getFormData($("#config-viz-form"), 0, query_id);
        json.push(mapChartData);
        viz_request = getMapVisualizationRequest(json);
        show_viz(viz_request)
    }
    ;
};

function getMapVisualizationRequest(json) {
    var viz_request = "/visualizations/get_map_visualization/?layer_count=1&";
    var url = "";
    for (var i = 0; i < json.length; i++) {
        var obj = json[i];
        for (var key in obj) {
            url += "&" + (key) + obj['layer_id'] + "=" + (obj[key]);
        }
    }
    url = url.replace("&", "");
    viz_request += url;
    return viz_request;
}

function show_viz(viz_request) {
    // language=HTML
    var htmlString = '<div class="outputLoadImg"><img src="/static/img/loading_gif.gif"/></div><iframe class="iframe-class" id="viz-iframe" src="' + viz_request + '" frameborder="0" allowfullscreen="" ></iframe>';
    $("#viz_container").html(htmlString);
    $('#myModal #submit-modal-btn').show();
    $("#viz_container .outputLoadImg").css("display", "block");
    $("#viz_container iframe").on("load", function () {
        $(this).siblings(".outputLoadImg").css("display", "none");
    });
}

function hide_gif() {
    $(".outputLoadImg").css("display", "none");
};

function getFormData(form, count, query) {
    var unindexed_array = form.serializeArray();
    var indexed_array = {};
    $.map(unindexed_array, function (n) {
        indexed_array[n['name']] = n['value'];
    });
    indexed_array['query'] = query;
    indexed_array['layer_id'] = String(count);
    indexed_array['cached_file_id'] = String(Math.floor(Date.now() / 1000)) + 'layer' + String(count);
    return indexed_array;
}