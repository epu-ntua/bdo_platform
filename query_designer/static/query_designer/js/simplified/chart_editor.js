// var query_id = $('#query-variables-select-container div').attr("id");
function hide_gif() {
        $(".outputLoadImg").css("display", "none");
    };
$(document).ready(function () {
    var selected_val = null;
    var var_list = null;
    var var_select = null;
    var col_select = null;
    var flag = false;
    $('[data-toggle="tooltip"]').tooltip();

    function updateVariables() {
        $('#query-variables-select-container').find('option').remove();
        $('#query-dimensions-select-container').find('option').remove();
        var record;
        $('#myModal .variable-select').find('option').remove();
        $('#myModal .variables-select ').find('option').remove();
        $('#myModal .column-select ').find('option').remove();
        $('#myModal .columns-select ').find('option').remove();
        $('#myModal .ais-select ').find('option').remove();
        var json_query_document = QueryToolbox.generateQueryDoc();
        var list_of_options_dims = [];

        for (var i = 0; i < json_query_document["from"].length; i++) {
            for (var j = 0; j < json_query_document["from"][i]["select"].length; j++) {
                record = json_query_document["from"][i]["select"][j];
                if ((record['exclude'] === false) || (record['exclude'] === '')) {
                    if (record['type'] === 'VALUE') {
                        $('#query-variables-select-container').append('<option value=' + String(record["name"]) + '>' + String(record["title"]) + '</option>');
                    }
                    else {
                        var flag = false;
                        for (var element in list_of_options_dims) {
                            if (String(record["title"]) === String(element)) {
                                flag = true;
                            }
                        }
                        if (flag === false) {
                            $('#query-dimensions-select-container').append('<option value=' + String(record["name"]) + '>' + String(record["title"]) + '</option>');
                            list_of_options_dims.push(String(record["title"]));
                        }
                    }
                }
            }
        }
        var variables_content = $('#query-variables-select-container').html();
        var dimensions_content = $('#query-dimensions-select-container').html();

        $('#myModal .variable-select ').html(variables_content);
        $('#myModal .variables-select ').html(variables_content);
        $('#myModal .column-select ').html(variables_content + dimensions_content);
        $('#myModal .columns-select ').html(variables_content + dimensions_content);
    }


    function populate_selects(){
        $('.popover-content #use_existing_temp_res').parent().checkbox().first().checkbox({
            onChecked: function(){
                $('.popover-content #temporal_resolution').parent().addClass('disabled');
            },
            onUnchecked: function () {
                $('.popover-content #temporal_resolution').parent().removeClass('disabled');
            }
        });
        $('.popover-content .checkbox').parent().removeClass('form-group label-floating');

        $('.popover-content #use_color_column').parent().checkbox().first().checkbox({
            onChecked: function(){
                $('.popover-content #color_var').parent().removeClass('disabled');
            },
            onUnchecked: function () {
                $('.popover-content #color_var').parent().addClass('disabled');
            }
        });
        // $('.popover-content .checkbox').parent().removeClass('form-group label-floating');

        $('.popover-content #select_all_columns').parent().checkbox().first().checkbox({
            onChecked: function(){
                const options = $('.popover-content .columns-select #column_choice> option').toArray().map(
                (obj) => obj.value
              );
              $('.popover-content .columns-select #column_choice').dropdown('set exactly', options);
            },
            onUnchecked: function() {
              $('.popover-content .columns-select #column_choice').dropdown('clear');
            },
        });

         $(".popover-content .variable-select").dropdown({
                clearable: true,
                placeholder: 'Select a Variable',
            });
        $(".popover-content .variable-select").dropdown('clear');

        $(".popover-content .column-select").dropdown({
            clearable: true,
            placeholder: 'Select a Variable or Dimension',

        });
        $(".popover-content .column-select").dropdown('clear');
        $(".popover-content .variables-select").dropdown({
            clearable: true,
            placeholder: 'Select Variable(s)',
        });

         $(".popover-content .columns-select").dropdown({
            clearable: true,
            placeholder: 'Select Variables or Dimensions',
        });

        $(".popover-content .aggregate-select").dropdown({
            placeholder: 'Select an Aggregate Function'
        });
        $(".popover-content .aggregate-select").dropdown('restore defaults');

        $(".popover-content .select-select").dropdown({
            placeholder: 'Select an Option'
        });
        $(".popover-content .select-select").dropdown('restore defaults');

        $(".popover-content .dataset-argument-select").dropdown({
            placeholder: 'Select one of the chosen arguments'
        });
        $(".popover-content .dataset-argument-select").dropdown('restore defaults');

        $(".control-label").css("margin-bottom","3px");

        $(".popover-content .column-select").dropdown('setting','onChange',function () {
            selected_val = $(".popover-content .column-select").dropdown('get value');
            var_list = $(".popover-content .variables-select").dropdown('get value');
            var_select = $(".popover-content .variable-select").dropdown('get value');
            if (((jQuery.inArray(selected_val,var_list)!== -1)||(selected_val===var_select))&&(selected_val!=='') && (selected_val!=null)){
                alert('Please choose a variable or dimension that is not already in use.');
                $(".popover-content .column-select").dropdown('clear');
                selected_val = null;
                col_select = null;
            }
         })

        $(".popover-content .variable-select").dropdown('setting','onChange',function () {
            selected_val = $(".popover-content .variable-select").dropdown('get value');
            var_list = $(".popover-content .variables-select").dropdown('get value');
            col_select = $(".popover-content .column-select").dropdown('get value');
            if (((jQuery.inArray(selected_val,var_list)!== -1)||(selected_val===col_select)) &&(selected_val!=='') && (selected_val!=null)){
                alert('Please choose a variable that is not already in use.');
                $(".popover-content .variable-select").dropdown('clear');
                selected_val = null;
                var_select = null;
            }
         })

        $(".popover-content .variables-select").dropdown('setting','onChange',function () {
            selected_val = $(".popover-content .variables-select").dropdown('get value');
            var_select = $(".popover-content .variable-select").dropdown('get value');
            col_select = $(".popover-content .column-select").dropdown('get value');
            flag = false;
            if (selected_val!==null && selected_val!=='' && selected_val!==undefined) {
                var limit = selected_val.length
                for (var i = 0; i < limit; i++) {
                    if (selected_val[i] === var_select) {
                        $(".popover-content .variable-select").dropdown('clear');
                        flag = true;
                        selected_val = null;
                        var_select = null;
                    }
                    if (selected_val[i] === col_select) {
                        $(".popover-content .column-select").dropdown('clear');
                        flag = true;
                        selected_val = null;
                        col_select = null;
                    }
                }
                if ((selected_val !== '') && (selected_val !== null) && flag) {
                    alert('Please choose a variable that is not already in use.');
                }
            }
         })
    }


    function specific_viz_form_configuration(){
        //PIE CHART
        var pie_chart_id = $('#viz_config ul li[data-viz-name="get_pie_chart_am"]').attr('data-viz-id');
        var pie_chart_agg_select = $('.popover-content #viz_'+pie_chart_id+' .aggregate-select');
        pie_chart_agg_select.dropdown('set selected' , 'COUNT');
        pie_chart_agg_select.find('option[value= "MAX"]').remove();
        pie_chart_agg_select.find('option[value= "MIN"]').remove();
        pie_chart_agg_select.find('option[value= "AVG"]').remove();

        //TIME SERIES
        var time_series_id = $('#viz_config ul li[data-viz-name="get_time_series_am"]').attr('data-viz-id');
        var time_series_checkbox = $('.popover-content #viz_'+time_series_id+' #use_existing_temp_res');
        time_series_checkbox.parent().checkbox('check');

        // PLOTLINE VESSEL COURSE
        var plotline_vessel_course_id = $('#viz_config ul li[data-viz-name="get_map_plotline_vessel_course"]').attr('data-viz-id');
        var plotline_vessel_course_input = $('.popover-content #viz_'+plotline_vessel_course_id+' #points_limit');
        var plotline_platform_id_input = $('.popover-content #viz_'+ plotline_vessel_course_id+' #platform_id');
        plotline_platform_id_input.val(' ');
        plotline_vessel_course_input.val(20);
        plotline_vessel_course_input.on('input',function () {
            if (plotline_vessel_course_input.val()>=10000 || plotline_vessel_course_input.val()<0){
                alert('Please set the limit of plotline points below 10000 and above 0.');
                plotline_vessel_course_input.val(20);
            }
        });
        // POLYGON LINE
        var polygon_id = $('#viz_config ul li[data-viz-name="get_map_polygon"]').attr('data-viz-id');
        var polygon_input = $('.popover-content #viz_'+polygon_id+' #points_limit');
        polygon_input.val(1);
        polygon_input.on('input',function () {
            if ( polygon_input.val()>=100000 ||  polygon_input.val()<0){
                alert('Please set the limit of polygon points below 100000 and above 0.');
                 polygon_input.val(1);
            }
        });
        //HEATMAP
        var heatmap_id = $('#viz_config ul li[data-viz-name="get_map_heatmap"]').attr('data-viz-id');
        var heatmap_input = $('.popover-content #viz_'+heatmap_id+' #points_limit');
        heatmap_input.val(30);
        heatmap_input.on('input',function () {
            if ( heatmap_input.val()>=10000 || heatmap_input.val()<0){
                alert('Please set the limit of heatmap points below 10000 and above 0.');
                heatmap_input.val(30);
            }
        });
        var heatmap_col_select = $('.popover-content #viz_'+heatmap_id+' #heat_col');
        heatmap_col_select.append('<option value="heatmap_frequency">Frequency</option>');
        heatmap_col_select.dropdown('refresh');
        heatmap_col_select.parent().dropdown('clear');

         //MAP MARKERS VESSEL COURSE
        var markers_vessel_id = $('#viz_config ul li[data-viz-name="get_map_markers_vessel_course"]').attr('data-viz-id');

        var markers_vessel_input = $('.popover-content #viz_'+ markers_vessel_id+' #marker_limit');
        var markers_platform_id_input = $('.popover-content #viz_'+ markers_vessel_id+' #platform_id');
        markers_platform_id_input.val(' ');
        markers_vessel_input.val(20);
        markers_vessel_input.on('input',function () {
            if ( markers_vessel_input.val()>=1000 || markers_vessel_input.val()<0){
                alert('Please set the limit of heatmap points below 1000 and above 0.');
                markers_vessel_input.val(20);
            }
        });
        var markers_vessel_color_var = $('.popover-content #viz_'+ markers_vessel_id+' #color_var').parent();
        markers_vessel_color_var.find('option[value= "i0_platform_id"]').remove();
        markers_vessel_color_var.dropdown('clear');
        $('.popover-content #color_var').parent().addClass('disabled');

         //MAP MARKERS GRID
        var markers_grid_id = $('#viz_config ul li[data-viz-name="get_map_markers_grid"]').attr('data-viz-id');

        var markers_grid_input = $('.popover-content #viz_'+ markers_grid_id+' #marker_limit');
        markers_grid_input.val(30);
        markers_grid_input.on('input',function () {
            if ( markers_grid_input.val()>=1000 || markers_grid_input.val()<0){
                alert('Please set the limit of heatmap points below 1000 and above 0.');
                markers_grid_input.val(30);
            }
        });
    }



    $(".viz_item").click(function () {
        $('.popover').hide();
        var component_id = $(this).attr('data-viz-id');
        var component_type = $(this).attr('data-viz-type');
        var component_selector = 'li[data-viz-id="' + component_id + '"]';
        $(component_selector).popover({
            html: true,
            title: $(this).text() + ' Visualisation' + '<i style="margin-left: 7px; color:#AAAAAA" id="viz_id_icon" class="fas fa-info-circle form_field_info" data-html="true" data-toggle="tooltip" title="' + $(this).attr('data-description') + '"></i>',
            trigger: 'manual',
            content: function () {
                return $('.all_viz_forms  #viz_' + String(component_id)).clone();
            }
        });
        updateVariables();

        $(component_selector).popover('show');
        var popover_component = $('.popover#' + $(this).attr('aria-describedby'));
        var viz_info_text = "";
        $(popover_component).find('label.form_field_info').each(function () {
            viz_info_text = viz_info_text + "\n-" + $(this).text() + ": " + $(this).attr('title');
        });
        $('#viz_id_icon').attr('title', $('#viz_id_icon').attr('title') + viz_info_text);

        $(component_selector).on("hidden.bs.popover", function (e) {
            selected_val = null;
            var_list = null;
            var_select = null;
            col_select = null;
            flag = false;
            var selects_in_popover = '.popover-content #viz_' + component_id;
            $(selects_in_popover).remove();
            $(component_selector).popover('destroy');

        });
        populate_selects();
        specific_viz_form_configuration();


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
            var viz_request = "/visualizations/" + $(component_selector).data('viz-name');
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
            var iframe = $(this).contents();
            iframe.find('.leaflet-control-layers.leaflet-control').trigger('mouseenter');
            iframe.find(".leaflet-control-layers-list .leaflet-control-layers-base label span").hide();
            iframe.find(".leaflet-control-layers-list .leaflet-control-layers-base label div").hide();
            iframe.find(".leaflet-control-layers-list .leaflet-control-layers-base label").append('<span style="display:block">Mapbox Layers</span>');

            iframe.find("#chartPaginationDiv").on('click', '#chartNextBtn', function () {
                var page = parseInt(iframe.find('#chartPaginationDiv').attr("page"));
                if (page >= 0) {
                    iframe.find('#chartPaginationDiv').find('#chartPrevBtn').prop('disabled', false);
                }
                hide_rows(page, iframe);
                page++;
                show_rows(page, iframe);
                iframe.find('#chartPaginationDiv').attr("page", page);
                lastPage = Math.floor(parseInt(iframe.find('#chartPaginationDiv').attr("lastidx")) / 50);
                if (page >= lastPage - 1) {
                    $(this).prop('disabled', true);
                }
            });

            iframe.find("#chartPaginationDiv").on('click', '#chartPrevBtn', function () {
                var page = parseInt(iframe.find('#chartPaginationDiv').attr("page"));
                lastPage = Math.floor(parseInt(iframe.find('#chartPaginationDiv').attr("lastidx")) / 50);
                if (page <= lastPage) {
                    iframe.find('#chartPaginationDiv').find('#chartNextBtn').prop('disabled', false);
                }
                hide_rows(page, iframe);
                page--;
                show_rows(page, iframe);
                iframe.find('#chartPaginationDiv').attr("page", page);
                if (page <= 0) {
                    $(this).prop('disabled', true);
                }
            });

            function hide_rows(page, iframe) {
                for (ix = page * 50; ix < (page + 1) * 50; ix++) {
                    iframe.find('.table > tbody > tr[page="' + ix + '"]').hide();
                }
            }

            function show_rows(page, iframe) {
                for (ix = page * 50; ix < (page + 1) * 50; ix++) {
                    iframe.find('.table > tbody > tr[page="' + ix + '"]').show();
                }
            }
        });
    }


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
});