// var query_id = $('#query-variables-select-container div').attr("id");

function updateVariables() {
    var record;
    $('#myModal .variable-select').find('option').remove();
    $('#myModal .variables-select').find('option').remove();
    $('.current_query_select_options').find('option').remove();
    var json_query_document = QueryToolbox.generateQueryDoc();
    // console.log(JSON.stringify(json_query_document));
    var list_of_options = [];
    // $('.current_query_select_options').append('<option value="">Select a Variable or Dimension</option>');
    for (var i=0; i<json_query_document["from"].length; i++){
        for (var j=0; j<json_query_document["from"][i]["select"].length; j++){
            record = json_query_document["from"][i]["select"][j];
            if((record['exclude'] === false)||(record['exclude']==='')){
                var flag = false;
                for (var element in list_of_options) {
                    if (String(record["title"]) === String(element)) {
                        flag = true;
                    }
                }
                if (flag === false) {
                    $('.current_query_select_options').append('<option value=' + String(record["name"]) + '>' + String(record["title"]) + '</option>');
                    list_of_options.push(String(record["title"]));
                }
            }
        }
    }
    var content = $('.current_query_select_options').html();

    $('#myModal .variable-select ').html(content);
    $('#myModal .variables-select ').html(content);

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

    function areAllFieldsFilled() {
        var result = true;
        var conf_popover_id = '#' + $(component_selector).attr('aria-describedby');
        var selects = $(conf_popover_id).find('.popover-content').find("select");
        $(selects).each(function () {
            let select = this;
            if ($(select).val() === "") {
                alert("Please fill all the fields of the form and resubmit!");
                result = false;
                return false;    //this is used for the break from each function
            }
        });
        return result
    }

    $(component_selector).popover('show');
    $(".popover-content .variable-select").dropdown({
        clearable: true,
        placeholder: 'Select a Variable or Dimension'

    });
    $(".popover-content .variable-select").dropdown('clear');
    $(".popover-content .variables-select").dropdown({
        clearable: true,
        placeholder: 'Select Variable(s) or Dimension(s)'
    });
    $(".popover-content .aggregate-select").dropdown({
        clearable: true,
        placeholder: 'Select an Aggregate Function'
    });
     $(".popover-content .aggregate-select").dropdown('clear');
    // $(".dropdown").css("margin","3px");
    $(".control-label").css("margin-bottom","3px");
    var popver_id = '#' + $(component_selector).attr('aria-describedby');
    $(popver_id + ' #select_conf_ok').click(function () {
        if (areAllFieldsFilled()) {
            $("#viz_config .list-group").children().each(function () {
                $(this).find("#selected_viz_span").hide();
            });
            $(component_selector).find("#selected_viz_span").show();
            submit_conf(component_selector, component_type);
            $(component_selector).popover("hide");
        }
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
        viz_request += '?' + chartData + '&query=' + $('#selected_query').attr('value');
        show_viz(viz_request);
    }
    else {
        var json = [];
        var mapChartData = getFormData($("#config-viz-form"), 0, $('#selected_query').attr('value'));
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