// var query_id = $('#query-variables-select-container div').attr("id");
$("#select_data_popover").click(function () {
    $('.df_viz_item').popover('hide');
});
// var widget_open_edit_modal = null;
// var widget_edit_id = null;
var new_dataframe_name = null;
var df_open_modal = false;

function hide_gif() {
    $(".outputLoadImg").css("display", "none");
}

$(document).ready(function () {
    $('#modal-tab-data').click(function(){
         $('#submit-df-btn').hide();
         df_refresh_visualisation_modal();
    });
    $('#selected_dataframe').on('input', function () {
        new_dataframe_name = $(this).val();
        if (($(this).val()==='')||($(this).val()===null)) {
            $('#addVizModal #df_viz_config .list-group').css('visibility','hidden');
        }else{
            $('#addVizModal #df_viz_config .list-group').show();
            $('#addVizModal #df_viz_config .list-group').css('visibility','visible');
            $('#df_viz_container').show();
        }
    })
    $('#dataframe .form-group').css('display','inline-block');
    var df_selected_val = null;
    var df_viz_success = null;
    var df_var_list = null;
    var df_viz_request = '';
    var df_var_select = null;
    var df_col_select = null;
    var df_flag = false;

    $('#df_layers-list ul').empty();
    $('#df_layers-list').dropdown();
    $('#df_layers-list-title-button').click(function () {
        $('#df_layers-list').trigger('click');
    });
    $("#selected_dataframe").val(null);
    var df_layer_count = 0;
    var df_layer_json = [];
    var df_json;
    var df_selected_visualization = null;
    var df_first_time = true ;
    var df_vis_created_flag = false;


    $("#df_add_layer_btn").parent().click(function () {
        $(this).hide();
        if((new_dataframe_name!==null)&&(df_selected_visualization!==null)) {
            alert("Layer is now saved. Please add a new layer!");
            $("#df_viz_config").find("ul").children().each(function (index) {
                if ($(this).attr("data-viz-type") != "map") {
                    $(this).addClass('disabled');
                }
            });
            $(".list-group").css('visibility','hidden');
            $("#df_viz_config .list-group").children().each(function () {
                $(this).find(".selected_viz_span").hide();
            });
            df_layer_json = [];
            for (var i = 0; i < df_json.length; i++) {
                var obj = df_json[i];
                df_layer_json.push({});
                for (var key in obj) {
                    df_layer_json[i][key] = obj[key];
                }
            }
            $("#df_layers-list ul").append('<li class="df_layer_list_element item" id=df_layer_list_element'+String(df_layer_count)+' style="pointer-events: none" role=\"presentation\"><span  class="col-10 " style="display:inline; margin-right: 5px; pointer-events: none;" role=\"menuitem\" tabindex=\"-1\" href=\"#\"> Dataframe Name: ' + $("#selected_dataframe").val() + ' / Visualization: ' + String(df_selected_visualization) + '</span><button id=df_layer_list_element_btn'+String(df_layer_count)+' style="display: inline; pointer-events: auto!important; padding:2px 5px; font-size:10px;" type="button" class="btn btn-xs btn-primary col-2"><i class="glyphicon glyphicon-remove"></i></button></li>');
            $(".df_layer_list_element #df_layer_list_element_btn"+String(df_layer_count)).click(function () {
                 $("#df_viz_config .list-group").children().each(function () {
                        $(this).find(".selected_viz_span").hide();
                 });
                var df_del_id = $(this).closest('li').attr('id');
                for (var i = 0; i < df_layer_json.length; i++) {
                    var obj = df_layer_json[i];
                    // alert(del_id.split('layer_list_element')[1]);
                    if (obj['layer_id']==df_del_id.split('df_layer_list_element')[1]){
                        df_layer_count = df_layer_count-1;
                        df_layer_json.splice(i,1);
                        $(this).closest('li').remove();
                        for(var j = i ; j < df_layer_json.length; j++){
                            $(".df_layer_list_element #df_layer_list_element_btn"+String(j+1)).closest('li').attr('id','df_layer_list_element'+String(j));
                            $(".df_layer_list_element #df_layer_list_element_btn"+String(j+1)).attr('id','df_layer_list_element_btn'+String(j));
                            obj = df_layer_json[j];
                            df_layer_json[j]['layer_id'] = df_layer_json[j]['layer_id']-1;
                        }
                        i=j;
                    }
                }
                df_mapVizUrlCreator(df_layer_json,df_layer_count,'map');
            });
            df_layer_count = df_layer_count+1;
        }
        else{
            alert("Please select data and add visualization!")
        }
        $('#df_layers-list li').removeClass('disabled');
        df_selected_visualization = null;
        new_dataframe_name = null;
        $("#selected_dataframe").val(null);
    });


    $(".df_viz_item").click(function (element) {

        if($('.popover').not('.tour').length) {
            $('.df_viz_item').popover('hide');
        }
        else {
            var df_component_id = $(this).attr('data-viz-id');
            var df_component_type = $(this).attr('data-viz-type');
            var df_component_selector = 'li[data-viz-id="' + df_component_id + '"]';
            $(df_component_selector).popover({
                html: true,
                title: $(this).text() + 'Visualisation' + '<i style="margin-left: 7px; color:#AAAAAA"  class="fas fa-info-circle form_field_info" data-html="true" data-toggle="tooltip" title="' + $(this).attr('data-description') + '"></i>',
                trigger: 'manual',
                content: function () {
                    return $('.all_viz_forms  #viz_' + String(df_component_id)).clone();
                }
            });
            var df_chosen_viz = $(this).attr('data-viz-name');
            df_updateVariables(df_chosen_viz, df_component_id, df_component_type, df_component_selector, df_createPopover);
            // createPopover(component_id, component_type, component_selector, populate_selects(specific_viz_form_configuration));
        }

    });

    function df_specific_viz_form_configuration(){
        //    DATAFRAMES ALL
        $('.df-simple-input i.dropdown.icon').remove();
        $('.df-multi-input i.dropdown.icon').remove();
        $('.df-simple-input').parent().find('label').css('top','-31px');




        //LINE-CHART
        var allow_line_chart_submit = [true,true,true,true];
        var line_chart_id = $('#df_viz_config ul li[data-viz-name="get_df_line_chart_am"]').attr('data-viz-id');
        var line_chart_y_select = $('.popover-content #viz_'+line_chart_id+' #y_var');
        line_chart_y_select.dropdown('setting','onAdd', function () {
            setTimeout(function () {
                 allow_line_chart_submit = df_missing_multi_parameter(line_chart_y_select,allow_line_chart_submit,'Y-Axis-Variable',0);
            },100);

        });
        line_chart_y_select.dropdown('setting','onRemove', function () {
            allow_line_chart_submit = df_missing_multi_parameter(line_chart_y_select,allow_line_chart_submit,'Y-Axis-Variable',0);
        });
        line_chart_y_select.dropdown('set selected',line_chart_y_select.find('option').val('-1'));
        line_chart_y_select.dropdown('refresh');
        line_chart_y_select.parent().dropdown('clear');
        line_chart_y_select.find('option').remove();
        line_chart_y_select.parent().dropdown('clear');
        var line_chart_y_unit = $('.popover-content #viz_'+line_chart_id+' #y_var_unit');
        line_chart_y_unit.dropdown('setting','onAdd', function () {
            setTimeout(function () {
                 allow_line_chart_submit = df_missing_multi_parameter(line_chart_y_unit,allow_line_chart_submit,'Y-Axis-Unit',1);
            },100);

        });
        line_chart_y_unit.dropdown('setting','onRemove', function () {
            allow_line_chart_submit = df_missing_multi_parameter(line_chart_y_unit,allow_line_chart_submit,'Y-Axis-Unit',1);
        });
        line_chart_y_unit.dropdown('set selected',line_chart_y_unit.find('option').val('-1'));
        line_chart_y_unit.dropdown('refresh');
        line_chart_y_unit.parent().dropdown('clear');
        line_chart_y_unit.find('option').remove();
        line_chart_y_unit.parent().dropdown('clear');

        var line_chart_x_select = $('.popover-content #viz_'+line_chart_id+' #x_var');
        line_chart_x_select.on('input',function () {
            allow_line_chart_submit = df_missing_parameter(line_chart_x_select,allow_line_chart_submit,'X-Axis-Variable',2);
        });
        var line_chart_x_unit = $('.popover-content #viz_'+line_chart_id+' #x_var_unit');
        line_chart_x_unit.on('input',function () {
            allow_line_chart_submit = df_missing_parameter(line_chart_x_unit,allow_line_chart_submit,'X-Axis-Unit',3);
        });
        $(line_chart_x_select).val('').trigger("input");
        $(line_chart_x_unit).val('').trigger("input");

        //COLUMN-CHART
        var allow_column_chart_submit = [true,true,true,true];
        var column_chart_id = $('#df_viz_config ul li[data-viz-name="get_df_column_chart_am"]').attr('data-viz-id');
        var column_chart_y_select = $('.popover-content #viz_'+column_chart_id+' #y_var');
        column_chart_y_select.dropdown('setting','onAdd', function () {
            setTimeout(function () {
                 allow_column_chart_submit = df_missing_multi_parameter(column_chart_y_select,allow_column_chart_submit,'Y-Axis-Variable',0);
            },100);

        });
        column_chart_y_select.dropdown('setting','onRemove', function () {
            allow_column_chart_submit = df_missing_multi_parameter(column_chart_y_select,allow_column_chart_submit,'Y-Axis-Variable',0);
        });
        column_chart_y_select.dropdown('set selected',column_chart_y_select.find('option').val('-1'));
        column_chart_y_select.dropdown('refresh');
        column_chart_y_select.parent().dropdown('clear');
        column_chart_y_select.find('option').remove();
        column_chart_y_select.parent().dropdown('clear');
        var column_chart_y_unit = $('.popover-content #viz_'+column_chart_id+' #y_var_unit');
        column_chart_y_unit.dropdown('setting','onAdd', function () {
            setTimeout(function () {
                 allow_column_chart_submit = df_missing_multi_parameter(column_chart_y_unit,allow_column_chart_submit,'Y-Axis-Unit',1);
            },100);

        });
        column_chart_y_unit.dropdown('setting','onRemove', function () {
            allow_column_chart_submit = df_missing_multi_parameter(column_chart_y_unit,allow_column_chart_submit,'Y-Axis-Unit',1);
        });
        column_chart_y_unit.dropdown('set selected',column_chart_y_unit.find('option').val('-1'));
        column_chart_y_unit.dropdown('refresh');
        column_chart_y_unit.parent().dropdown('clear');
        column_chart_y_unit.find('option').remove();
        column_chart_y_unit.parent().dropdown('clear');

        var column_chart_x_select = $('.popover-content #viz_'+column_chart_id+' #x_var');
        column_chart_x_select.on('input',function () {
            allow_column_chart_submit = df_missing_parameter(column_chart_x_select,allow_column_chart_submit,'X-Axis-Variable',2);
        });
        var column_chart_x_unit = $('.popover-content #viz_'+column_chart_id+' #x_var_unit');
        column_chart_x_unit.on('input',function () {
            allow_column_chart_submit = df_missing_parameter(column_chart_x_unit,allow_column_chart_submit,'X-Axis-Unit',3);
        });
        $(column_chart_x_select).val('').trigger("input");
        $(column_chart_x_unit).val('').trigger("input");

        //TIMESERIES
        var allow_timeseries_chart_submit = [true,true];
        var timeseries_chart_id = $('#df_viz_config ul li[data-viz-name="get_df_time_series_am"]').attr('data-viz-id');
        var timeseries_chart_y_select = $('.popover-content #viz_'+timeseries_chart_id+' #y_var');
        timeseries_chart_y_select.dropdown('setting','onAdd', function () {
            setTimeout(function () {
                 allow_line_chart_submit = df_missing_multi_parameter(timeseries_chart_y_select,allow_line_chart_submit,'Y-Axis-Variable',0);
            },100);

        });
        timeseries_chart_y_select.dropdown('setting','onRemove', function () {
            allow_line_chart_submit = df_missing_multi_parameter(timeseries_chart_y_select,allow_line_chart_submit,'Y-Axis-Variable',0);
        });
        timeseries_chart_y_select.dropdown('set selected',timeseries_chart_y_select.find('option').val('-1'));
        timeseries_chart_y_select.dropdown('refresh');
        timeseries_chart_y_select.parent().dropdown('clear');
        timeseries_chart_y_select.find('option').remove();
        timeseries_chart_y_select.parent().dropdown('clear');
        var timeseries_chart_y_unit = $('.popover-content #viz_'+timeseries_chart_id+' #y_var_unit');
        timeseries_chart_y_unit.dropdown('setting','onAdd', function () {
            setTimeout(function () {
                 allow_line_chart_submit = df_missing_multi_parameter(timeseries_chart_y_unit,allow_line_chart_submit,'Y-Axis-Unit',1);
            },100);

        });
        timeseries_chart_y_unit.dropdown('setting','onRemove', function () {
            allow_line_chart_submit = df_missing_multi_parameter(timeseries_chart_y_unit,allow_line_chart_submit,'Y-Axis-Unit',1);
        });
        timeseries_chart_y_unit.dropdown('set selected',timeseries_chart_y_unit.find('option').val('-1'));
        timeseries_chart_y_unit.dropdown('refresh');
        timeseries_chart_y_unit.parent().dropdown('clear');
        timeseries_chart_y_unit.find('option').remove();
        timeseries_chart_y_unit.parent().dropdown('clear');

      //  HISTOGRAM

        var allow_histogram_submit = [true,true];
        var histogram_id = $('#df_viz_config ul li[data-viz-name="get_df_histogram_chart_am"]').attr('data-viz-id');
        var histogram_input = $('.popover-content #viz_'+histogram_id+' #bins');
        var viz_conf_histogram = viz_conf_json['visualiser']['histogram_chart_am'];
        histogram_input.val(viz_conf_histogram['default_bins']);
        histogram_input.on('input',function () {
            allow_histogram_submit = df_limit_points(histogram_input,viz_conf_histogram,allow_histogram_submit,'bins',1)
        });

        var histogram_variable_select = $('.popover-content #viz_'+histogram_id+' #x_var');
        histogram_variable_select.on('input',function () {
            allow_histogram_submit = df_missing_parameter(histogram_variable_select,allow_histogram_submit,'variable',0);
        });
        $(histogram_variable_select).val('').trigger("input");


      //  HEATMAP
        var allow_heatmap_submit = [true,true,true];
        var heatmap_id = $('#df_viz_config ul li[data-viz-name="get_df_map_heatmap"]').attr('data-viz-id');
        var viz_conf_heatmap = viz_conf_json['visualiser']['map_heatmap'];
        var heatmap_col_select = $('.popover-content #viz_'+heatmap_id+' #heat_col');
        heatmap_col_select.on('input',function () {
            allow_heatmap_submit = df_missing_parameter(heatmap_col_select,allow_heatmap_submit,'variable',0);
        });
        $(heatmap_col_select).val('').trigger("input");
        var heatmap_lat_col = $('.popover-content #viz_'+heatmap_id+' #lat_col');
        heatmap_lat_col.on('input',function () {
            allow_heatmap_submit = df_missing_parameter(heatmap_lat_col,allow_heatmap_submit,'latitude-column',1);
        });
        $(heatmap_lat_col).val('').trigger("input");
        var heatmap_lon_col = $('.popover-content #viz_'+heatmap_id+' #lon_col');
        heatmap_lon_col.on('input',function () {
            allow_heatmap_submit = df_missing_parameter(heatmap_lon_col,allow_heatmap_submit,'longitude-column',2);
        });
        $(heatmap_lon_col).val('').trigger("input");

      //  MARKERS GRID
        var allow_markers_grid_submit = [true,true,true,true];
        var markers_grid_id = $('#df_viz_config ul li[data-viz-name="get_df_map_markers_grid"]').attr('data-viz-id');

        var markers_grid_col_select = $('.popover-content #viz_'+markers_grid_id+' #variable');
        markers_grid_col_select.on('input',function () {
            allow_markers_grid_submit = df_missing_parameter(markers_grid_col_select,allow_markers_grid_submit,'variable',0);
        });
        $(markers_grid_col_select).val('').trigger("input");
        var markers_grid_unit = $('.popover-content #viz_'+markers_grid_id+' #var_unit');
        markers_grid_unit.on('input',function () {
            allow_markers_grid_submit = df_missing_parameter(markers_grid_unit,allow_markers_grid_submit,'variable-unit',1);
        });
        $(markers_grid_unit).val('').trigger("input");
        var markers_grid_lat_col = $('.popover-content #viz_'+markers_grid_id+' #lat_col');
        markers_grid_lat_col.on('input',function () {
            allow_markers_grid_submit = df_missing_parameter(markers_grid_lat_col,allow_markers_grid_submit,'latitude-column',2);
        });
        $(markers_grid_lat_col).val('').trigger("input");
        var markers_grid_lon_col = $('.popover-content #viz_'+markers_grid_id+' #lon_col');
        markers_grid_lon_col.on('input',function () {
            allow_markers_grid_submit = df_missing_parameter(markers_grid_lon_col,allow_markers_grid_submit,'longitude-column',3);
        });
        $(markers_grid_lon_col).val('').trigger("input");



      //MAP MARKERS VESSEL COURSE
        var markers_checkbox_flag = false;
        var allow_markers_vessel_submit = [true, true, true];
        $('.popover-content #use_color_column').parent().parent().css('margin-top','0px');
        $('.popover-content #use_color_column').parent().checkbox().first().checkbox({
            onChecked: function(){
                $('.popover-content #color_var').parent().removeClass('disabled');
                markers_checkbox_flag = true;
                allow_markers_vessel_submit = df_missing_parameter(markers_vessel_color_var, allow_markers_vessel_submit, 'color-column', 2);
            },
            onUnchecked: function () {
                $('.popover-content #color_var').parent().addClass('disabled');
                $('.popover-content #color_var').val(null);
                markers_checkbox_flag = false;
                allow_markers_vessel_submit[2] = true;
                $('.color-column_missing_error').remove();

                var flag = true;
                for (var el=0; el<allow_markers_vessel_submit.length;el++){
                    if (allow_markers_vessel_submit[el]===false){
                        flag = false;
                    }
                }
                if (flag=== true){
                    $('#dataframe #select_conf_ok').removeClass('disabled');
                }

            }
        });
        var markers_vessel_id = $('#df_viz_config ul li[data-viz-name="get_df_map_markers_vessel_course"]').attr('data-viz-id');
        var markers_vessel_input = $('.popover-content #viz_'+ markers_vessel_id+' #marker_limit');
        var viz_conf_markers_vessel = viz_conf_json['visualiser']['map_markers_vessel_course'];
        var markers_vessel_col_id_select = $('.popover-content #viz_'+markers_vessel_id+' #vessel-id-columns-select');
        var markers_vessel_col_select = $('.popover-content #viz_'+markers_vessel_id+' #variable');
        var markers_vessel_id_select = $('.popover-content #viz_'+markers_vessel_id+' #vessel-id');

        var markers_vessel_color_var = $('.popover-content #viz_'+ markers_vessel_id+' #color_var');
        $('.popover-content #color_var').parent().addClass('disabled');
        markers_vessel_color_var.on('input',function () {
            if (markers_checkbox_flag) {
                allow_markers_vessel_submit = df_missing_parameter(markers_vessel_color_var, allow_markers_vessel_submit, 'color-column', 2);
            }
        });
        var markers_vessel_var = $('.popover-content #viz_'+ markers_vessel_id+' #variable');
        markers_vessel_var.on('input',function () {
                allow_markers_vessel_submit = df_missing_parameter(markers_vessel_var, allow_markers_vessel_submit, 'variable', 0);
        });
        var markers_vessel_var_unit = $('.popover-content #viz_'+ markers_vessel_id+' #var_unit');
        markers_vessel_var_unit.on('input',function () {
                allow_markers_vessel_submit = df_missing_parameter(markers_vessel_var_unit, allow_markers_vessel_submit, 'variable-unit', 1);
        });
        $(markers_vessel_var_unit).val('').trigger("input");
        $(markers_vessel_var).val('').trigger("input");


    //CONTOURS ON MAP
        var allow_contour_submit = [true,true,true,true,true];
        var contour_id = $('#df_viz_config ul li[data-viz-name="get_df_map_contour"]').attr('data-viz-id');
        var contours_input = $('.popover-content #viz_'+contour_id+' #n_contours');
        var viz_conf_contour = viz_conf_json['visualiser']['map_contour'];
        contours_input.val(viz_conf_contour['default_contours']);
        contours_input.on('input',function () {
            allow_contour_submit = df_limit_points(contours_input, viz_conf_contour, allow_contour_submit, 'contours',4);
        });
        var contour_col_select = $('.popover-content #viz_'+contour_id+' #contour_var');
        contour_col_select.on('input',function () {
            allow_contour_submit = df_missing_parameter(contour_col_select,allow_contour_submit,'variable',0);
        });
        $(contour_col_select).val('').trigger("input");
        var contour_col_unit = $('.popover-content #viz_'+contour_id+' #contour_var_unit');
        contour_col_unit.on('input',function () {
            allow_contour_submit = df_missing_parameter(contour_col_unit,allow_contour_submit,'variable-unit',1);
        });
        $(contour_col_unit).val('').trigger("input");
        var contour_lat_col = $('.popover-content #viz_'+contour_id+' #lat_col');
        contour_lat_col.on('input',function () {
            allow_contour_submit = df_missing_parameter(contour_lat_col,allow_contour_submit,'latitude-column',2);
        });
        $(contour_lat_col).val('').trigger("input");
        var contour_lon_col = $('.popover-content #viz_'+contour_id+' #lon_col');
        contour_lon_col.on('input',function () {
            allow_contour_submit = df_missing_parameter(contour_lon_col,allow_contour_submit,'longitude-column',3);
        });
        $(contour_lon_col).val('').trigger("input");

    // //    PIECHART
    //     var df_pie_chart_id = $('#df_viz_config ul li[data-viz-name="get_df_pie_chart_am"]').attr('data-viz-id');
    //     var df_pie_chart_agg_select = $('.popover-content #viz_'+df_pie_chart_id+' .aggregate-select');
    //     df_pie_chart_agg_select.dropdown('set selected' , 'COUNT');
    //     df_pie_chart_agg_select.find('option[value= "MAX"]').remove();
    //     df_pie_chart_agg_select.find('option[value= "MIN"]').remove();
    //     df_pie_chart_agg_select.find('option[value= "AVG"]').remove();





    }


    function df_createPopover(component_id, component_type, component_selector){
        $(component_selector).on("hidden.bs.popover", function(e) {
            $(".df_viz_item").removeClass('waiting-disable');
            df_selected_val = null;
            df_var_list = null;
            df_var_select = null;
            df_col_select = null;
            df_flag = false;
            var df_selects_in_popover = '.popover-content #viz_' + component_id;
            $(df_selects_in_popover).remove();
            $(component_selector).popover('destroy');

        });
        $(component_selector).on("shown.bs.popover", function(e) {
            $(".df_viz_item").removeClass('waiting-disable');
            df_populate_selects(df_specific_viz_form_configuration);
        });
        $(component_selector).popover('show');
        var popover_component = $('.popover#'+$(this).attr('aria-describedby'));
        var viz_info_text = "";
        $(popover_component).find('label.form_field_info').each(function () {
            viz_info_text = viz_info_text + "\n-"+$(this).text()+": " + $(this).attr('title');
        });



        var popver_id = '#' + $(component_selector).attr('aria-describedby');
        $(popver_id + ' #select_conf_ok').click(function (e) {
            df_open_modal=true;
            df_selected_visualization = $(component_selector).text();
            $("#df_viz_config .list-group").children().each(function () {
                $(this).find(".selected_viz_span").hide();
            });
            $(component_selector).find(".selected_viz_span").show();

            df_submit_conf(component_selector, component_type);
            $(component_selector).popover("hide");
        });
        $(popver_id + ' #select_conf_cancel').click(function (e) {
            $(component_selector).popover("hide");
        });

    }

    function df_updateVariables(chosen_viz,component_id, component_type, component_selector,_callback){
            _callback(component_id, component_type, component_selector);
    }

    function df_populate_selects(_mycallback){
        $('.df-multi-input').dropdown({
          allowAdditions: true,
            keys: {
              delimiter: 32
            }
        });
        $(".popover-content .aggregate-select").dropdown({
            placeholder: 'Select an Aggregate Function'
        });
        $(".popover-content .aggregate-select").dropdown('restore defaults');

        $(".popover-content .select-select").dropdown({
            placeholder: 'Select an Option'
        });
        $(".popover-content .select-select").dropdown('restore defaults');

        _mycallback();
    }

    function df_submit_conf(component_selector,component_type) {
        var df_conf_popover_id;
        var df_submitted_args;
        var df_selects;
        var df_myData;
        $('#df_add_layer_btn').parent().hide();
        $('#df_layers-list').parent().hide();
        $('#addVizModal #submit-df-btn').hide();
        if(component_type!='map') {
            var viz_request = "/visualizations/";
            viz_request += $('#addVizModal').find('.modal-body').find('div#viz_'+ String($(component_selector).attr('data-viz-id'))).find('#action').val().replace('df_','');
            df_conf_popover_id = '#' + $(component_selector).attr('aria-describedby');
            df_submitted_args = $('#addVizModal').find(df_conf_popover_id).find('.popover-content').clone();
            df_selects = $('#addVizModal').find(df_conf_popover_id).find('.popover-content').find("select");
            $(df_selects).each(function (i) {
                var select = this;
                $(df_submitted_args).find("select").eq(i).val($(select).val());
                $('#config-viz-form').append(select);
            });

            $('#config-viz-form').empty();
            $('#config-viz-form').append(df_submitted_args);
            df_myData = $("#config-viz-form").serialize();
            viz_request += '?';
            viz_request += df_myData;
            viz_request += '&df=' + $('#addVizModal #selected_dataframe').val()+'&notebook_id='+String(notebook_id_for_url);
            df_vis_created_flag = true;
            show_viz(viz_request, component_type,1);
        }
        else{
            df_conf_popover_id = '#' + $(component_selector).attr('aria-describedby');
            df_submitted_args = $('#addVizModal').find(df_conf_popover_id).find('.popover-content').clone();
            df_selects = $('#addVizModal').find(df_conf_popover_id).find('.popover-content').find("select");
            $(df_selects).each(function (i) {
                var select = this;
                $(df_submitted_args).find("select").eq(i).val($(select).val());
                $('#config-viz-form').append(select);
            });
            $('#config-viz-form').empty();
            $('#config-viz-form').append(df_submitted_args);
            df_myData = df_getFormData($("#config-viz-form"),df_layer_count,$('#addVizModal #selected_dataframe').val());
            df_json=[];
            for (var i = 0; i < df_layer_json.length; i++) {
                var obj = df_layer_json[i];
                df_json.push({});
                for (var key in obj) {
                    df_json[i][key] = obj[key];
                }
            }
            df_json.push(df_myData);
            if (df_first_time){
                df_mapVizUrlCreator(df_json, df_layer_count + 1, component_type);
            }
            else{
                df_first_time = false;
                df_mapVizUrlCreator(df_json, df_layer_count, component_type);
            }
        };
        df_vis_created_flag = true;

    };
    function df_mapVizUrlCreator(json,my_layer_count, comp_type){
        var viz_request = "/visualizations/get_map_visualization/?";
        viz_request += "layer_count="+String(my_layer_count)+"&";
        var url="";
        for (var i = 0; i < json.length; i++) {
            var obj =json[i];
            for (var key in obj) {
                if (key.includes('[]')){
                    for (var jcount = 0; jcount<obj[key].length; jcount++) {
                        url = url + "&" + (key.replace('[]', '')) + obj['layer_id'] + "[]" + "=" + (obj[key][jcount]);
                    }
                }else {
                    url = url + "&" + (key) + obj['layer_id'] + "=" + (obj[key]);
                }
            }
        }
        url = url.replace("&","");
        viz_request += url;
        show_viz(viz_request, comp_type, String(my_layer_count));
    }

    function df_getFormData(form,count,df){
        var unindexed_array = form.serializeArray();
        var indexed_array = {};
        $.map(unindexed_array, function(n, i){
            if(n['name'].includes('[]')){
                if(indexed_array.hasOwnProperty(n['name'])){
                    indexed_array[n['name']].push(n['value']);
                }else{
                    indexed_array[n['name']] = [n['value']];
                }
            }else {
                if(n['name']==='action'){
                    indexed_array[n['name']] =  n['value'].replace('df_','')
                }else {
                    indexed_array[n['name']] = n['value'];
                }
            }
        });
        indexed_array['df'] = df;
        indexed_array['layer_id'] = String(count);
        indexed_array['cached_file_id'] = String(Math.floor(Date.now() / 1000))+'layer'+String(count) ;
        return indexed_array;
    }
    // function getFormData(form,count,query){
    //     var unindexed_array = form.serializeArray();
    //     var indexed_array = {};
    //     $.map(unindexed_array, function(n, i){
    //         if(n['name'].includes('[]')){
    //             if(indexed_array.hasOwnProperty(n['name'])){
    //                 indexed_array[n['name']].push(n['value']);
    //             }else{
    //                 indexed_array[n['name']] = [n['value']];
    //             }
    //         }else {
    //             indexed_array[n['name']] = n['value'];
    //         }
    //     });
    //     indexed_array['query'] = query;
    //     indexed_array['layer_id'] = String(count);
    //     indexed_array['cached_file_id'] = String(Math.floor(Date.now() / 1000))+'layer'+String(count) ;
    //     return indexed_array;
    // }
    function show_viz(viz_request, comp_type, layer_count) {
        $("#df_viz_container").html('<div class="loadingFrame"><img src="' + img_source_path + '"/></div><iframe class="iframe-class" id="df-viz-iframe" ' +
            'src="' + viz_request + '" frameborder="0" allowfullscreen="" ' +
            '></iframe>');



        // $('#addVizModal #submit-modal-btn').show();
        $("#addVizModal #df_viz_container .loadingFrame").css( "display", "block" );
        $("#addVizModal #df_viz_container iframe").on( "load", function(){
            $(this).siblings(".loadingFrame").css( "display", "none" );
            var execution_flag = $(this).contents().find('.visualisation_execution_input').val();

            if ((execution_flag === 'success')&&(comp_type === 'map')&&(df_open_modal === true)){
                $('#df_add_layer_btn').parent().show();
                $('#df_layers-list').parent().show();
                $('#addVizModal #submit-df-btn').show();
                var map_iframe = $(this).contents();
                map_iframe.find('.leaflet-control-layers.leaflet-control').trigger('mouseenter');
                map_iframe.find(".leaflet-control-layers-list .leaflet-control-layers-base label span").hide();
                map_iframe.find(".leaflet-control-layers-list .leaflet-control-layers-base label div").hide();
                map_iframe.find(".leaflet-control-layers-list .leaflet-control-layers-base label").append('<span style="display:block">Mapbox Layers</span>');

            }else if((execution_flag === 'success')&&(comp_type !== 'map')&&(df_open_modal === true)){
                $('#addVizModal #submit-df-btn').show();
                $('#df_add_layer_btn').parent().hide();
                $('#df_layers-list').parent().hide();
                var iframe = $(this).contents();
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
            }
            else{
                $('#df_add_layer_btn').parent().hide();
                $('#df_layers-list').parent().hide();
                $('#addVizModal #submit-df-btn').hide();
            }
        });
    }

     $("#dismiss-modal-btn").click(function m(e) {
        df_refresh_visualisation_modal();
        $('#select_viz_popover').prop('disabled', true);
        $('#select_conf_popover').prop('disabled', true);
        // $('#addVizModal #viz_container').html('<div class="loadingFrame">' +
        //     '                    <img src="' + img_source_path + '"/>' +
        //     '                </div>');
    });

    $("#addVizModal #submit-df-btn").click(function () {
        if (df_vis_created_flag!==false){
            df_refresh_visualisation_modal();
        }else{
            alert('Please create a Visualisation first.')
        }
    });


    function df_refresh_visualisation_modal(){
        df_open_modal = false;
        $('#df_layers-list ul').empty();
        $("#selected_dataframe").val(null);
        df_layer_count = 0;
        df_layer_json = [];
        df_selected_visualization = null;
        df_first_time = true ;
        df_vis_created_flag = false;
        $('#addVizModal #df_viz_config #df_add_layer_btn').parent().hide();
        $('#addVizModal #df_viz_config #df_layers-list').parent().hide();
        $("#df_viz_config .list-group").children().each(function () {
            $(this).find(".selected_viz_span").hide();
        });
        $("#df_viz_config").find("ul").children().each(function (index) {
                $(this).removeClass('disabled');
        });
        $('.df_viz_item').popover('hide');
        $('#addVizModal #df_viz_config .list-group').hide();
        $('#addVizModal #df_viz_config #df_viz_container').hide();
        $("#addVizModal #df_viz_container").empty();
        $("#submit-df-btn").hide();


    }



    function df_missing_parameter(col_select, allow_submit,parameter_name,parameter_id){
        if((col_select.val()=== null)||(col_select.val()==='')||(col_select.val().trim()==='')){
                if(allow_submit[parameter_id]===true) {
                    $('#dataframe #select_conf_ok').addClass('disabled');
                    $("<div class='conf-error-message "+parameter_name+"_missing_error'>* Selection of "+ parameter_name +" is required.</div>").insertBefore("#dataframe #select_conf_ok");
                }
                allow_submit[parameter_id] = false;
            }
            else{
                allow_submit[parameter_id] = true;
                $('.'+parameter_name+'_missing_error').remove();
                if(df_check_list(allow_submit)){
                    $('#dataframe #select_conf_ok').removeClass('disabled');
                }
            }
        return allow_submit
    }


    function df_limit_points(input, viz_conf, allow_submit, unit, parameter_id){
        if (input.val()>viz_conf['limit'] || input.val()<=0 || (input.val()==='')){
                if(allow_submit[parameter_id]===true) {
                    $("<div class='conf-error-message limit_oob_message'>* Number of "+unit+" must be below " + String(viz_conf['limit']) + " and above 0.</div>").insertBefore("#dataframe #select_conf_ok");
                    $('#dataframe #select_conf_ok').addClass('disabled');
                }
                allow_submit[parameter_id] = false;
            }else{
                allow_submit[parameter_id] = true;
                $('.limit_oob_message').remove();
                if(df_check_list(allow_submit)) {
                    $('#dataframe #select_conf_ok').removeClass('disabled');
                }
            }
        return allow_submit
    }

    function df_missing_multi_parameter(col_select, allow_submit,parameter_name,parameter_id){

        if((col_select.val()=== null)||(col_select.val().length===0)){
                if(allow_submit[parameter_id]===true) {
                    $('#dataframe #select_conf_ok').addClass('disabled');
                    $("<div class='conf-error-message "+parameter_name+"_missing_error'>* Selection of "+ parameter_name +" is required.</div>").insertBefore("#dataframe #select_conf_ok");
                }
                allow_submit[parameter_id] = false;
            }
            else{
                allow_submit[parameter_id] = true;
                $('.'+parameter_name+'_missing_error').remove();
                if(df_check_list(allow_submit)){
                    $('#dataframe #select_conf_ok').removeClass('disabled');
                }
            }
        return allow_submit
    }

    function df_check_list(list){
        var flag = true;
        for(var i=0; i<list.length; i++){
            if(list[i]===false){
                flag=false;
            }
        }
        return flag;
    }

    // tour = tour_guide_senario('', '');
    $('#addVizModal').on('shown.bs.modal', function (e) {
        init = 1;
        // tour = tour_guide_senario(tour, "");
    })



});



