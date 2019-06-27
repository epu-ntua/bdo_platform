var tour;
$("#select_data_popover").click(function () {
            $('.viz_item').popover('hide');
        });
        var widget_open_edit_modal = null;
        var widget_edit_id = null;
        var open_modal= false;
        var new_query_id;
        // {#Variable to store active ckeditor version #}
        var textEditNote = CKEDITOR.appendTo('change_note');
        var textEditor = CKEDITOR.appendTo('viz_note');
        var contour_flag = false;
        // {#Function to change tabs in modal from data to notes and create new ckeditor instance if it doesnt exist#}
        $(document).ready(function () {
            var init = 0;
            var viz_success = null;
            var selected_val = null;
            var var_list = null;
            var var_select = null;
            var col_select = null;
            var flag = false;
            $('[data-toggle="tooltip"]').tooltip();

            $('#layers-list ul').empty();
            $('#layers-list').dropdown();
            $('#layers-list-title-button').click(function () {
                $('#layers-list').trigger('click');
            });

            $("#query_name_span").text(null);
            var layer_count = 0;
            var layer_json = [];
            var json;
            var selected_visualization = null;
            var first_time = true ;
            var vis_created_flag = false;

            $("#new_widget_btn").click(function () {
                $("#myModal #viz_container").empty();
                $('#myModal #submit-modal-btn').hide();
                $('#myModal #add_layer_btn').parent().hide();
                $('#myModal #layers-list').parent().hide();

            });
            $("#add_layer_btn").parent().click(function () {
                if (selected_visualization.trim()==='Contours On Map'){
                    contour_flag = true;
                }
                init = 6;
                tour = tour_guide_senario(tour,'');
                $(this).hide();
                if((new_query_id!=null)&&(selected_visualization!=null)) {
                    alert("Layer is now saved. Please add a new layer!");
                    $("#viz_config").find("ul").children().each(function (index) {
                        if ($(this).attr("data-viz-type") != "map") {
                            $(this).addClass('disabled');
                        }
                        if (contour_flag&&($(this).attr("data-viz-name") === "get_map_contour")){
                            $(this).addClass('disabled');
                        }
                    });
                    $(".list-group").css('visibility','hidden');
                    $("#viz_config .list-group").children().each(function () {
                        $(this).find("#selected_viz_span").hide();
                    });
                    layer_json = [];
                    for (var i = 0; i < json.length; i++) {
                        var obj = json[i];
                        layer_json.push({});
                        for (var key in obj) {
                            layer_json[i][key] = obj[key];
                        }
                    }

                    $("#layers-list ul").append('<li class="layer_list_element item" id=layer_list_element'+String(layer_count)+' style="pointer-events: none" role=\"presentation\"><span  class="col-10 " style="display:inline; margin-right: 5px; pointer-events: none;" role=\"menuitem\" tabindex=\"-1\" href=\"#\"> Visualization: ' + String(selected_visualization)+ ' -- Query Name: ' + $("#query_name_span").text() + '</span><button id=layer_list_element_btn'+String(layer_count)+' style="display: inline; pointer-events: auto!important; padding:2px 5px; font-size:10px;" type="button" class="btn btn-xs btn-primary col-2"><i class="glyphicon glyphicon-remove"></i></button></li>');
                    $(".layer_list_element #layer_list_element_btn"+String(layer_count)).click(function () {
                         $("#viz_config .list-group").children().each(function () {
                                $(this).find("#selected_viz_span").hide();
                         });
                        var del_id = $(this).closest('li').attr('id');
                        for (var i = 0; i < layer_json.length; i++) {
                            var obj = layer_json[i];
                            // alert(del_id.split('layer_list_element')[1]);
                            if (obj['layer_id']==del_id.split('layer_list_element')[1]){
                                layer_count = layer_count-1;
                                layer_json.splice(i,1);
                                $(this).closest('li').remove();
                                for(var j = i ; j < layer_json.length; j++){
                                    $(".layer_list_element #layer_list_element_btn"+String(j+1)).closest('li').attr('id','layer_list_element'+String(j));
                                    $(".layer_list_element #layer_list_element_btn"+String(j+1)).attr('id','layer_list_element_btn'+String(j));
                                    obj = layer_json[j];
                                    layer_json[j]['layer_id'] = layer_json[j]['layer_id']-1;
                                }
                                i=j;
                            }
                        }
                        mapVizUrlCreator(layer_json,layer_count,'map');
                    });
                    layer_count = layer_count+1;
                }
                else{
                    alert("Please select data and add visualization!")
                }
                $('#layers-list li').removeClass('disabled');
                selected_visualization = null;
                new_query_id = null;
                $("#query_name_span").text(null);
            });
            $("#myModal #modal-tab-notes").click(function (e) {
                $('#submit-note-btn').show();
                $('#submit-modal-btn').hide();
                if(textEditor == null) {
                    textEditor = CKEDITOR.appendTo('viz_note');
                }
            });
            $("#myModal #modal-tab-data").click(function (e) {
                $('#submit-note-btn').hide();
                if(vis_created_flag) {
                    $('#submit-modal-btn').show();
                }
            });
            $("#myModal #select_data_popover").popover({
                html: true,
                animation: true,
                title: 'Select query to use',
                content: function () {
                    return $('#query-container').html();
                }
            }).click(function (e) {
                if ($('#layers-list ul li').length===0) {
                    init = 2;
                }else{
                    init = 7;
                }
                tour = tour_guide_senario(tour, "");
                $(this).popover('toggle');
                $('.popover-content .form-group #query-select').dropdown();

                $('.popover-content #select_data_ok').click(function (e) {
                    new_query_id = $(".popover-content #query-select").dropdown('get value');
                    var new_query_text = $(".popover-content #query-select").dropdown('get text');
                    $('#myModal #selected_query').val(new_query_id);
                    $('#query_name_span').show();
                    $('#query_name_span').text(new_query_text);
                    $('#myModal #select_data_popover').popover("hide");
                    $('#myModal #viz_config .list-group').show();
                    $('#myModal #viz_config #viz_container').show();
                    // $('#add_layer_btn').parent().hide();
                    // $('#layers-list').parent().hide();
                    $(".list-group").css('visibility','visible');
                    if ($('#layers-list ul li').length===0) {
                        init = 3;
                    }else{
                        init = 8;
                    }
                    tour = tour_guide_senario(tour, "");
                });
                $('.popover-content #select_data_cancel').click(function (e) {
                    $('#myModal #select_data_popover').popover("hide");
                })
            });

            $(".viz_item").click(function (element) {
                if ($('#layers-list ul li').length===0) {
                        init = 4;
                    }else{
                        init = 9;
                    }
                tour = tour_guide_senario(tour, "");
                if($('.popover').not('.tour').length) {
                    $('.viz_item').popover('hide');
                }
                else {
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
                    var chosen_viz = $(this).attr('data-viz-name');
                    updateVariables(chosen_viz, component_id, component_type, component_selector, createPopover);
                    // createPopover(component_id, component_type, component_selector, populate_selects(specific_viz_form_configuration));
                }

            });

            function specific_viz_form_configuration(){

                //AGGREGATE-VALUE
                var allow_aggregate_value_submit = [true];
                var aggregate_value_id = $('#viz_config ul li[data-viz-name="get_aggregate_value"]').attr('data-viz-id');
                var aggregate_value_col_select = $('.popover-content #viz_'+aggregate_value_id+' #variable');
                aggregate_value_col_select.on('change',function () {
                    allow_aggregate_value_submit = missing_parameter(aggregate_value_col_select,allow_aggregate_value_submit,'variable',0);
                });
                aggregate_value_col_select.dropdown('refresh');
                aggregate_value_col_select.parent().dropdown('clear');


                //DATA-TABLE
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
                var allow_datatable_submit = [true];
                var datatable_id = $('#viz_config ul li[data-viz-name="get_data_table"]').attr('data-viz-id');
                var datatable_col_select = $('.popover-content #viz_'+datatable_id+' #column_choice');
                datatable_col_select.on('change',function () {
                    allow_datatable_submit = missing_parameter(datatable_col_select,allow_datatable_submit,'column',0);
                });
                datatable_col_select.dropdown('set selected',datatable_col_select.find('option').val());
                datatable_col_select.dropdown('refresh');
                datatable_col_select.parent().dropdown('clear');


                //HISTOGRAM
                var allow_histogram_submit = [true,true];
                var histogram_id = $('#viz_config ul li[data-viz-name="get_histogram_chart_am"]').attr('data-viz-id');
                var histogramm_select = $('.popover-content #viz_'+histogram_id+' .column-select');
                var histogram_input = $('.popover-content #viz_'+histogram_id+' #bins');
                var viz_conf_histogram = viz_conf_json['visualiser']['histogram_chart_am'];
                histogram_input.val(viz_conf_histogram['default_bins']);
                histogram_input.on('input',function () {
                    allow_histogram_submit = limit_points(histogram_input,viz_conf_histogram,allow_histogram_submit,'bins',1)
                });
                histogramm_select.find('option').each(function () {
                    if ($(this).val().includes('time')){
                        $(this).remove();
                    }
                });
                var histogram_variable_select = $('.popover-content #viz_'+histogram_id+' #x_var');
                histogram_variable_select.on('change',function () {
                    allow_histogram_submit = missing_parameter(histogram_variable_select,allow_histogram_submit,'variable',0);
                });
                histogram_variable_select.dropdown('refresh');
                histogram_variable_select.parent().dropdown('clear');


                 //HISTOGRAM2D
                var allow_histogram2d_submit = [true,true,true];
                var histogram2d_id = $('#viz_config ul li[data-viz-name="get_histogram_2d_am"]').attr('data-viz-id');
                var histogramm2d_select = $('.popover-content #viz_'+histogram2d_id+' .column-select');
                var histogram2d_input = $('.popover-content #viz_'+histogram2d_id+' #bins');
                var viz_conf_histogram2d = viz_conf_json['visualiser']['histogram_2d_am'];
                histogram2d_input.val(viz_conf_histogram2d['default_bins']);
                histogram2d_input.on('input',function () {
                    allow_histogram2d_submit = limit_points(histogram2d_input,viz_conf_histogram2d,allow_histogram2d_submit,'bins',0)
                });
                histogramm2d_select.find('option').each(function () {
                    if ($(this).val().includes('time')){
                        $(this).remove();
                    }
                });
                var histogram2d_yvariable_select = $('.popover-content #viz_'+histogram2d_id+' #y_var');
                histogram2d_yvariable_select.on('change',function () {
                    allow_histogram2d_submit = missing_parameter(histogram2d_yvariable_select,allow_histogram2d_submit,'Y-Axis-Variable',1);
                });
                histogram2d_yvariable_select.dropdown('refresh');
                histogram2d_yvariable_select.parent().dropdown('clear');

                var histogram2d_xvariable_select = $('.popover-content #viz_'+histogram2d_id+' #x_var');
                histogram2d_xvariable_select.on('change',function () {
                    allow_histogram2d_submit = missing_parameter(histogram2d_xvariable_select,allow_histogram2d_submit,'X-Axis-Variable',2);
                });
                histogram2d_xvariable_select.dropdown('refresh');
                histogram2d_xvariable_select.parent().dropdown('clear');


                //PIE CHART
                var allow_pie_chart_submit = [true,true];
                var pie_chart_id = $('#viz_config ul li[data-viz-name="get_pie_chart_am"]').attr('data-viz-id');
                var pie_chart_agg_select = $('.popover-content #viz_'+pie_chart_id+' .aggregate-select');
                pie_chart_agg_select.dropdown('set selected' , 'COUNT');
                pie_chart_agg_select.find('option[value= "MAX"]').remove();
                pie_chart_agg_select.find('option[value= "MIN"]').remove();
                pie_chart_agg_select.find('option[value= "AVG"]').remove();
                var pie_chart_col_select = $('.popover-content #viz_'+pie_chart_id+' #value_var');
                pie_chart_col_select.on('change',function () {
                    allow_pie_chart_submit = missing_parameter(pie_chart_col_select,allow_pie_chart_submit,'variable',0);
                });
                pie_chart_col_select.dropdown('refresh');
                pie_chart_col_select.parent().dropdown('clear');
                var pie_chart_separator_select = $('.popover-content #viz_'+pie_chart_id+' #key_var');
                pie_chart_separator_select.on('change',function () {
                    allow_pie_chart_submit = missing_parameter(pie_chart_separator_select,allow_pie_chart_submit,'separator',1);
                });
                pie_chart_separator_select.dropdown('set selected',pie_chart_separator_select.find('option').val());
                pie_chart_separator_select.dropdown('refresh');
                pie_chart_separator_select.parent().dropdown('clear');


                //LINE-CHART
                var allow_line_chart_submit = [true,true];
                var line_chart_id = $('#viz_config ul li[data-viz-name="get_line_chart_am"]').attr('data-viz-id');
                var line_chart_y_select = $('.popover-content #viz_'+line_chart_id+' #y_var');
                line_chart_y_select.on('change',function () {
                    allow_line_chart_submit = missing_parameter(line_chart_y_select,allow_line_chart_submit,'Y-Axis-Variable',0);
                });
                line_chart_y_select.dropdown('set selected',line_chart_y_select.find('option').val());
                line_chart_y_select.dropdown('refresh');
                line_chart_y_select.parent().dropdown('clear');
                var line_chart_x_select = $('.popover-content #viz_'+line_chart_id+' #x_var');
                line_chart_x_select.on('change',function () {
                    allow_line_chart_submit = missing_parameter(line_chart_x_select,allow_line_chart_submit,'X-Axis-Variable',1);
                });
                line_chart_x_select.dropdown('refresh');
                line_chart_x_select.parent().dropdown('clear');


                //COLUMN-CHART
                var allow_column_chart_submit = [true,true];
                var column_chart_id = $('#viz_config ul li[data-viz-name="get_column_chart_am"]').attr('data-viz-id');
                var column_chart_y_select = $('.popover-content #viz_'+column_chart_id+' #y_var');
                column_chart_y_select.on('change',function () {
                    allow_column_chart_submit = missing_parameter(column_chart_y_select,allow_column_chart_submit,'Y-Axis-Variable',0);
                });
                column_chart_y_select.dropdown('set selected',column_chart_y_select.find('option').val());
                column_chart_y_select.dropdown('refresh');
                column_chart_y_select.parent().dropdown('clear');
                var column_chart_x_select = $('.popover-content #viz_'+column_chart_id+' #x_var');
                column_chart_x_select.on('change',function () {
                    allow_column_chart_submit = missing_parameter(column_chart_x_select,allow_column_chart_submit,'X-Axis-Variable',1);
                });
                column_chart_x_select.dropdown('refresh');
                column_chart_x_select.parent().dropdown('clear');


                //TIME SERIES
                 $('.popover-content #use_existing_temp_res').parent().checkbox().first().checkbox({
                    onChecked: function(){
                        $('.popover-content #temporal_resolution').parent().addClass('disabled');
                    },
                    onUnchecked: function () {
                        $('.popover-content #temporal_resolution').parent().removeClass('disabled');
                    }
                });
                $('.popover-content .checkbox').parent().removeClass('form-group label-floating');

                // $('.popover-content .checkbox').parent().removeClass('form-group label-floating');
                var allow_time_series_submit = [true];
                var time_series_id = $('#viz_config ul li[data-viz-name="get_time_series_am"]').attr('data-viz-id');
                var time_series_checkbox = $('.popover-content #viz_'+time_series_id+' #use_existing_temp_res');
                time_series_checkbox.parent().checkbox('check');
                var time_series_col_select = $('.popover-content #viz_'+time_series_id+' #y_var');
                time_series_col_select.on('change',function () {
                    allow_time_series_submit = missing_parameter(time_series_col_select,allow_time_series_submit,'variable',0);
                });
                time_series_col_select.dropdown('set selected',time_series_col_select.find('option').val());
                time_series_col_select.dropdown('refresh');
                time_series_col_select.parent().dropdown('clear');


                // PLOTLINE VESSEL COURSE
                var allow_plotline_submit = [true, true, true];
                var plotline_vessel_course_id = $('#viz_config ul li[data-viz-name="get_map_plotline_vessel_course"]').attr('data-viz-id');
                var plotline_vessel_course_input = $('.popover-content #viz_'+plotline_vessel_course_id+' #points_limit');
                var plotline_platform_id_input = $('.popover-content #viz_'+ plotline_vessel_course_id+' #platform_id');
                var viz_conf_plotline = viz_conf_json['visualiser']['map_plotline_vessel_course'];
                var plotline_vessel_id_select = $('.popover-content #viz_'+plotline_vessel_course_id+' #vessel-id');
                plotline_platform_id_input.val(' ');
                plotline_vessel_course_input.val(viz_conf_plotline['default_points']);
                plotline_vessel_course_input.on('input',function () {
                    allow_plotline_submit = limit_points(plotline_vessel_course_input,viz_conf_plotline,allow_plotline_submit,'positions',0);
                });
                aggregate_value_col_select.parent().dropdown('clear');
                var plotline_vessel_col_id_select = $('.popover-content #viz_'+plotline_vessel_course_id+' #vessel-id-columns-select');
                plotline_vessel_col_id_select.on('change', function(){
                    allow_plotline_submit = missing_parameter(plotline_vessel_col_id_select, allow_plotline_submit, 'Vessel-ID-Column',1 )
                    if ((plotline_vessel_col_id_select.val()!== '')&&(plotline_vessel_col_id_select.val()!==null)){
                        plotline_vessel_id_select.parent().removeClass('disabled');
                        plotline_vessel_id_select.find('option').remove();
                        $('.vessel-id-select option[data-type="'+ String(plotline_vessel_col_id_select.val())+'"]').clone().appendTo('.popover-content #vessel-id');
                        plotline_vessel_id_select.parent().dropdown('clear');
                    }else{
                        plotline_vessel_id_select.find('option').remove();
                        plotline_vessel_id_select.parent().dropdown('clear');
                        plotline_vessel_id_select.parent().addClass('disabled');
                    }
                });
                plotline_vessel_col_id_select.parent().dropdown('clear');
                plotline_vessel_id_select.on('change', function(){
                    allow_plotline_submit = missing_parameter(plotline_vessel_id_select, allow_plotline_submit, 'Vessel-ID', 2 )
                });
                plotline_vessel_id_select.parent().dropdown('clear');
                plotline_vessel_id_select.parent().addClass('disabled');


                //CONTOURS
                var allow_contour_submit = [true,true];
                var contour_id = $('#viz_config ul li[data-viz-name="get_map_contour"]').attr('data-viz-id');
                var contours_input = $('.popover-content #viz_'+contour_id+' #n_contours');
                var viz_conf_contour = viz_conf_json['visualiser']['map_contour'];
                contours_input.val(viz_conf_contour['default_contours']);
                contours_input.on('input',function () {
                    allow_contour_submit = limit_points(contours_input, viz_conf_contour, allow_contour_submit, 'contours',1);
                });
                var contour_col_select = $('.popover-content #viz_'+contour_id+' #contour_var');
                contour_col_select.on('change',function () {
                    allow_contour_submit = missing_parameter(contour_col_select,allow_contour_submit,'variable',0);
                });
                contour_col_select.dropdown('refresh');
                contour_col_select.parent().dropdown('clear');


                // POLYGON LINE
                var allow_polygon_submit = [true];
                var polygon_id = $('#viz_config ul li[data-viz-name="get_map_polygon"]').attr('data-viz-id');
                var polygon_input = $('.popover-content #viz_'+polygon_id+' #points_limit');
                var viz_conf_polygon = viz_conf_json['visualiser']['map_polygon'];
                polygon_input.val(viz_conf_polygon['default_points']);
                polygon_input.on('input',function () {
                        allow_polygon_submit = limit_points(polygon_input,viz_conf_polygon,allow_polygon_submit,'points',0);
                });


                //HEATMAP
                // var allow_heatmap_submit = [true,true];
                var allow_heatmap_submit = [true];
                var heatmap_id = $('#viz_config ul li[data-viz-name="get_map_heatmap"]').attr('data-viz-id');
                // var heatmap_points_input = $('.popover-content #viz_'+heatmap_id+' #points_limit');
                var viz_conf_heatmap = viz_conf_json['visualiser']['map_heatmap'];
                // heatmap_points_input.val(viz_conf_heatmap['default_points']);
                // heatmap_points_input.on('input',function () {
                //     allow_heatmap_submit = limit_points(heatmap_points_input, viz_conf_heatmap, allow_heatmap_submit, 'points',1);
                // });
                var heatmap_col_select = $('.popover-content #viz_'+heatmap_id+' #heat_col');
                heatmap_col_select.append('<option value="heatmap_frequency">Frequency</option>');
                heatmap_col_select.on('change',function () {
                    allow_heatmap_submit = missing_parameter(heatmap_col_select,allow_heatmap_submit,'variable',0);
                });
                heatmap_col_select.dropdown('refresh');
                heatmap_col_select.parent().dropdown('clear');


                 //MAP MARKERS VESSEL COURSE
                var markers_checkbox_flag = false;
                var allow_markers_vessel_submit = [true, true, true, true, true];
                 $('.popover-content #use_color_column').parent().checkbox().first().checkbox({
                    onChecked: function(){
                        $('.popover-content #color_var').parent().removeClass('disabled');
                        markers_checkbox_flag = true;
                        allow_markers_vessel_submit = missing_parameter(markers_vessel_color_var, allow_markers_vessel_submit, 'color-column', 4);

                    },
                    onUnchecked: function () {
                        $('.popover-content #color_var').parent().addClass('disabled');
                        $('.popover-content #color_var').dropdown('clear');
                        markers_checkbox_flag = false;
                        allow_markers_vessel_submit[4] = true;
                        $('.color-column_missing_error').remove();

                        var flag = true;
                        for (var el=0; el<allow_markers_vessel_submit.length;el++){
                            if (allow_markers_vessel_submit[el]===false){
                                flag = false;
                            }
                        }
                        if (flag=== true){
                            $('#select_conf_ok').removeClass('disabled');
                        }

                    }
                });
                var markers_vessel_id = $('#viz_config ul li[data-viz-name="get_map_markers_vessel_course"]').attr('data-viz-id');
                var markers_vessel_input = $('.popover-content #viz_'+ markers_vessel_id+' #marker_limit');
                var viz_conf_markers_vessel = viz_conf_json['visualiser']['map_markers_vessel_course'];
                var markers_vessel_col_id_select = $('.popover-content #viz_'+markers_vessel_id+' #vessel-id-columns-select');
                var markers_vessel_col_select = $('.popover-content #viz_'+markers_vessel_id+' #variable');
                var markers_vessel_id_select = $('.popover-content #viz_'+markers_vessel_id+' #vessel-id');
                markers_vessel_input.val(viz_conf_markers_vessel['default_points']);
                markers_vessel_input.on('input',function () {
                    allow_markers_vessel_submit = limit_points(markers_vessel_input,viz_conf_markers_vessel,allow_markers_vessel_submit,'markers',1)
                });
                var markers_vessel_color_var = $('.popover-content #viz_'+ markers_vessel_id+' #color_var');
                markers_vessel_color_var.find('option[value= "i0_longitude"]').remove();
                markers_vessel_color_var.find('option[value= "i0_latitude"]').remove();
                markers_vessel_color_var.find('option[value= "i0_time"]').remove();
                $('.popover-content #color_var').parent().addClass('disabled');
                markers_vessel_color_var.on('change',function () {
                    if (markers_checkbox_flag) {
                        allow_markers_vessel_submit = missing_parameter(markers_vessel_color_var, allow_markers_vessel_submit, 'color-column', 4);
                    }
                });
                markers_vessel_color_var.dropdown('clear');
                markers_vessel_col_select.on('change',function () {
                    allow_markers_vessel_submit = missing_parameter(markers_vessel_col_select, allow_markers_vessel_submit,'variable',0);
                });
                markers_vessel_col_select.dropdown('refresh');
                markers_vessel_col_select.parent().dropdown('clear');


                markers_vessel_col_id_select.on('change', function(){
                    allow_markers_vessel_submit = missing_parameter(markers_vessel_col_id_select, allow_markers_vessel_submit, 'Vessel-ID-Column',2 )
                    if ((markers_vessel_col_id_select.val()!== '')&&(markers_vessel_col_id_select.val()!==null)){
                        markers_vessel_id_select.parent().removeClass('disabled');
                        markers_vessel_id_select.find('option').remove();
                        $('.vessel-id-select option[data-type="'+ String(markers_vessel_col_id_select.val())+'"]').clone().appendTo('.popover-content #vessel-id');
                    }else{
                        $('.popover-content #vessel-id').append('<option value=1>test</option>');
                        setTimeout(function() {
                            markers_vessel_id_select.dropdown('set selected',markers_vessel_id_select.find('option').val());
                            markers_vessel_id_select.parent().dropdown('clear');
                            markers_vessel_id_select.find('option').remove();
                            markers_vessel_id_select.parent().addClass('disabled');
                        }, 20);
                    }
                });
                markers_vessel_col_id_select.parent().dropdown('clear');
                markers_vessel_id_select.on('change', function(){
                    allow_markers_vessel_submit = missing_parameter(markers_vessel_id_select, allow_markers_vessel_submit, 'Vessel-ID', 3 )
                });




        //LIVE AIS
                var allow_live_ais_submit = [true, true];
                var live_ais_id = $('#viz_config ul li[data-viz-name="get_live_ais"]').attr('data-viz-id');
                var live_ais_vessel_col_id_select = $('.popover-content #viz_'+live_ais_id+' #vessel-id-columns-select');
                // var live_ais_vessel_col_select = $('.popover-content #viz_'+live_ais_id+' #variable');
                var live_ais_vessel_id_select = $('.popover-content #viz_'+live_ais_id+' #vessel-id');

                live_ais_vessel_col_id_select.on('change', function(){
                    allow_live_ais_submit = missing_parameter(live_ais_vessel_col_id_select, allow_live_ais_submit, 'Vessel-ID-Column',0 )
                    if ((live_ais_vessel_col_id_select.val()!== '')&&(live_ais_vessel_col_id_select.val()!==null)){
                        live_ais_vessel_id_select.parent().removeClass('disabled');
                        live_ais_vessel_id_select.find('option').remove();
                        $('.vessel-id-select option[data-type="'+ String(live_ais_vessel_col_id_select.val())+'"]').clone().appendTo('.popover-content #vessel-id');

                    }else{
                        $('.popover-content #vessel-id').append('<option value=1>test</option>');
                        setTimeout(function() {
                            live_ais_vessel_id_select.dropdown('set selected',live_ais_vessel_id_select.find('option').val());
                            live_ais_vessel_id_select.parent().dropdown('clear');
                            live_ais_vessel_id_select.find('option').remove();
                            live_ais_vessel_id_select.parent().addClass('disabled');
                        }, 20);
                    }
                });
                live_ais_vessel_col_id_select.parent().dropdown('clear');
                live_ais_vessel_id_select.on('change', function(){
                    allow_live_ais_submit = missing_parameter(live_ais_vessel_id_select, allow_live_ais_submit, 'Vessel-ID', 1 )
                });
                 //MAP MARKERS GRID
                var allow_markers_grid_submit = [true,true];
                var markers_grid_id = $('#viz_config ul li[data-viz-name="get_map_markers_grid"]').attr('data-viz-id');
                var markers_grid_input = $('.popover-content #viz_'+ markers_grid_id+' #marker_limit');
                var viz_conf_markers_grid = viz_conf_json['visualiser']['map_markers_grid'];
                markers_grid_input.val(viz_conf_markers_grid['default_points']);
                markers_grid_input.on('input',function () {
                    allow_markers_grid_submit = limit_points(markers_grid_input,viz_conf_markers_grid,allow_markers_grid_submit,'markers',1);
                });

                var markers_grid_col_select = $('.popover-content #viz_'+markers_grid_id+' #variable');
                markers_grid_col_select.on('change',function () {
                    allow_markers_grid_submit = missing_parameter(markers_grid_col_select,allow_markers_grid_submit,'variable',0);
                });
                markers_grid_col_select.dropdown('set selected',markers_grid_col_select.find('option').val());
                markers_grid_col_select.dropdown('refresh');
                markers_grid_col_select.parent().dropdown('clear');

            }

            function createPopover(component_id, component_type, component_selector){
                $(component_selector).on("hidden.bs.popover", function(e) {
                    $(".viz_item").removeClass('waiting-disable');
                    selected_val = null;
                    var_list = null;
                    var_select = null;
                    col_select = null;
                    flag = false;
                    var selects_in_popover = '.popover-content #viz_' + component_id;
                    $(selects_in_popover).remove();
                    $(component_selector).popover('destroy');

                });
                $(component_selector).on("shown.bs.popover", function(e) {
                    $(".viz_item").removeClass('waiting-disable');
                    populate_selects(specific_viz_form_configuration);
                });
                $(component_selector).popover('show');
                var popover_component = $('.popover#'+$(this).attr('aria-describedby'));
                var viz_info_text = "";
                $(popover_component).find('label.form_field_info').each(function () {
                    viz_info_text = viz_info_text + "\n-"+$(this).text()+": " + $(this).attr('title');
                });
                $('#viz_id_icon').attr('title',  $('#viz_id_icon').attr('title')+viz_info_text);


                // setTimeout(function () {
                //     specific_viz_form_configuration();
                // },150);



                var popver_id = '#' + $(component_selector).attr('aria-describedby');
                $(popver_id + ' #select_conf_ok').click(function (e) {
                    open_modal=true;
                    selected_visualization = $(component_selector).text();
                    $("#viz_config .list-group").children().each(function () {
                        $(this).find("#selected_viz_span").hide();
                    })
                    $(component_selector).find("#selected_viz_span").show();

                    submit_conf(component_selector, component_type);
                    $(component_selector).popover("hide");
                });
                $(popver_id + ' #select_conf_cancel').click(function (e) {
                    $(component_selector).popover("hide");
                });

            }

            function updateVariables(chosen_viz,component_id, component_type, component_selector,_callback){
                $('#myModal .variable-select').find('option').remove();
                $('#myModal .variables-select ').find('option').remove();
                $('#myModal .column-select ').find('option').remove();
                $('#myModal .columns-select ').find('option').remove();
                $('#myModal .variable-numeric-select').find('option').remove();
                $('#myModal .variables-numeric-select ').find('option').remove();
                $('#myModal .column-numeric-select ').find('option').remove();
                $('#myModal .columns-numeric-select ').find('option').remove();
                $('#myModal .vessel-id-columns-select ').find('option').remove();
                $('#myModal .vessel-id-select ').find('option').remove();
                $('#myModal .ais-select ').find('option').remove();
                var variables_content = $('#query-variables-select-container #'+String(new_query_id)).html();
                var dimensions_content = $('#query-dimensions-select-container #'+String(new_query_id)).html();
                var variables_numeric_content = '';
                var dimensions_numeric_content = '';
                $.each($('#query-variables-select-container #'+String(new_query_id)).find('option'), function (i, el) {
                    if(($(el).data('datatype') === "FLOAT") || ($(el).data('datatype') === "INT")  || ($(el).data('datatype') === "DOUBLE")  || ($(el).data('datatype') === "BYTE")){
                        variables_numeric_content += $(el).prop('outerHTML');
                    }
                });
                $.each($('#query-dimensions-select-container #'+String(new_query_id)).find('option'), function (i, el) {
                    if(($(el).data('datatype') === "FLOAT") || ($(el).data('datatype') === "INT")  || ($(el).data('datatype') === "DOUBLE")  || ($(el).data('datatype') === "BYTE")){
                        dimensions_numeric_content += $(el).prop('outerHTML');
                    }
                });
                // var dataset_arguments_content = $('#query-datasets-extra-arguments #'+String(new_query_id)).html();
                $('#myModal .variable-select ').html(variables_content);
                $('#myModal .variables-select ').html(variables_content);
                $('#myModal .column-select ').html(variables_content + dimensions_content);
                $('#myModal .columns-select ').html(variables_content + dimensions_content);
                $('#myModal .variable-numeric-select ').html(variables_numeric_content);
                $('#myModal .variables-numeric-select ').html(variables_numeric_content);
                $('#myModal .column-numeric-select ').html(variables_numeric_content + dimensions_numeric_content);
                $('#myModal .columns-numeric-select ').html(variables_numeric_content + dimensions_numeric_content);
                // $("#myModal .dataset-argument-select").html(dataset_arguments_content);
                if((chosen_viz ==='get_map_plotline_vessel_course')||(chosen_viz==='get_map_markers_vessel_course')|| (chosen_viz==='get_live_ais')) {
                    $(".viz_item").addClass('waiting-disable');
                    $.ajax({
                        "type": "GET",
                        "url": "/visualizations/get_vessel_ids_info/" + String(new_query_id) + "/",
                        "success": function (result) {
                            console.log(result);
                            $.each(result, function (col_name, values_list) {
                                $('#myModal .vessel-id-columns-select').append("<option value='" + col_name + "'>" + col_name + "</option>");
                                $.each(values_list, function (_, id_value) {
                                    $('#myModal .vessel-id-select').append("<option data-type='"+ String(col_name) +"' value='" + id_value + "'>" + id_value + "</option>");
                                });
                            });
                        },
                        "error": function () {
                            console.log('error getting vessel identifiers');
                        },
                        "complete": function (data) {
                            _callback(component_id, component_type, component_selector);
                        }
                    });
                }else{
                    _callback(component_id, component_type, component_selector);
                }

            }
            function populate_selects(_mycallback){


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

                $(".popover-content .variable-numeric-select").dropdown({
                        clearable: true,
                        placeholder: 'Select a Variable',
                    });
                $(".popover-content .variable-numeric-select").dropdown('clear');

                $(".popover-content .column-numeric-select").dropdown({
                    clearable: true,
                    placeholder: 'Select a Variable or Dimension',

                });
                $(".popover-content .column-numeric-select").dropdown('clear');
                $(".popover-content .variables-numeric-select").dropdown({
                    clearable: true,
                    placeholder: 'Select Variable(s)',
                });

                 $(".popover-content .columns-numeric-select").dropdown({
                    clearable: true,
                    placeholder: 'Select Variables or Dimensions',
                });

                $(".popover-content .vessel-id-columns-select").dropdown({
                    clearable: true,
                    placeholder: 'Select the column to use as vessel identifier',
                });

                $(".popover-content .vessel-id").dropdown({
                    clearable: true,
                    placeholder: 'Select the vessel identifier',
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
                 });

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
                 });

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
                _mycallback();

            }

            function submit_conf(component_selector,component_type) {
                var conf_popover_id;
                var submitted_args;
                var selects;
                var myData;
                $('#add_layer_btn').parent().hide();
                $('#layers-list').parent().hide();
                $('#myModal #submit-modal-btn').hide();
                if(component_type!='map') {
                    var viz_request = "/visualizations/";
                    viz_request += $('#myModal').find('.modal-body').find('#action').val();
                    conf_popover_id = '#' + $(component_selector).attr('aria-describedby');
                    submitted_args = $('#myModal').find(conf_popover_id).find('.popover-content').clone();
                    selects = $('#myModal').find(conf_popover_id).find('.popover-content').find("select");
                    $(selects).each(function (i) {
                        var select = this;
                        $(submitted_args).find("select").eq(i).val($(select).val());
                        $('#config-viz-form').append(select);
                    });
                    $('#config-viz-form').empty();
                    $('#config-viz-form').append(submitted_args);
                    myData = $("#config-viz-form").serialize();
                    alert(myData);
                    viz_request += '?';
                    viz_request += myData;
                    viz_request += '&query=' + $('#myModal #selected_query').val();
                    vis_created_flag = true;
                    show_viz(viz_request, component_type,1);
                }
                else{
                    conf_popover_id = '#' + $(component_selector).attr('aria-describedby');
                    submitted_args = $('#myModal').find(conf_popover_id).find('.popover-content').clone();
                    selects = $('#myModal').find(conf_popover_id).find('.popover-content').find("select");
                    $(selects).each(function (i) {
                        var select = this;
                        $(submitted_args).find("select").eq(i).val($(select).val());
                        $('#config-viz-form').append(select);
                    });
                    $('#config-viz-form').empty();
                    $('#config-viz-form').append(submitted_args);
                    myData = getFormData($("#config-viz-form"),layer_count,$('#myModal #selected_query').val());
                    json=[];
                    for (var i = 0; i < layer_json.length; i++) {
                        var obj = layer_json[i];
                        json.push({});
                        for (var key in obj) {
                            json[i][key] = obj[key];
                        }
                    }
                    json.push(myData);
                    if (first_time){
                        mapVizUrlCreator(json, layer_count + 1, component_type);
                    }
                    else{
                        first_time = false;
                        mapVizUrlCreator(json, layer_count, component_type);
                    }
                };
                vis_created_flag = true;

            };
            function mapVizUrlCreator(json,my_layer_count, comp_type){
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
            function getFormData(form,count,query){
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
                        indexed_array[n['name']] = n['value'];
                    }
                });
                indexed_array['query'] = query;
                indexed_array['layer_id'] = String(count);
                indexed_array['cached_file_id'] = String(Math.floor(Date.now() / 1000))+'layer'+String(count) ;
                return indexed_array;
            }
            function show_viz(viz_request, comp_type, layer_count) {
                $("#viz_container").html('<div class="loadingFrame"><img src="' + img_source_path + '"/></div><iframe class="iframe-class" id="viz-iframe" ' +
                    'src="' + viz_request + '" frameborder="0" allowfullscreen="" ' +
                    '></iframe>');


                // $('#myModal #submit-modal-btn').show();
                $("#myModal #viz_container .loadingFrame").css( "display", "block" );
                $("#myModal #viz_container iframe").on( "load", function(){
                    $(this).siblings(".loadingFrame").css( "display", "none" );
                    var execution_flag = $(this).contents().find('.visualisation_execution_input').val();

                    if ((execution_flag === 'success')&&(comp_type === 'map')&&(open_modal === true)){
                        $('#add_layer_btn').parent().show();
                        $('#layers-list').parent().show();
                        $('#myModal #submit-modal-btn').show();
                        // var map_iframe = $(this).contents();
                        // map_iframe.find('.leaflet-control-layers.leaflet-control').trigger('mouseenter');
                        // map_iframe.find(".leaflet-control-layers-list .leaflet-control-layers-base label span").hide();
                        // map_iframe.find(".leaflet-control-layers-list .leaflet-control-layers-base label div").hide();
                        // map_iframe.find(".leaflet-control-layers-list .leaflet-control-layers-base label").append('<span style="display:block">Mapbox Layers</span>');
                        if(layer_count==='1') {
                            init = 5;
                        }else{
                            init = 10;
                        }
                        tour = tour_guide_senario(tour,comp_type);
                    }else if((execution_flag === 'success')&&(comp_type !== 'map')&&(open_modal === true)){
                        $('#myModal #submit-modal-btn').show();
                        $('#add_layer_btn').parent().hide();
                        $('#layers-list').parent().hide();
                        var iframe = $(this).contents();
                        // iframe.find("#chartPaginationDiv").on('click', '#chartNextBtn', function () {
                        //     var page = parseInt(iframe.find('#chartPaginationDiv').attr("page"));
                        //     if (page >= 0) {
                        //         iframe.find('#chartPaginationDiv').find('#chartPrevBtn').prop('disabled', false);
                        //     }
                        //     hide_rows(page, iframe);
                        //     page++;
                        //     show_rows(page, iframe);
                        //     iframe.find('#chartPaginationDiv').attr("page", page);
                        //     lastPage = Math.floor(parseInt(iframe.find('#chartPaginationDiv').attr("lastidx")) / 50);
                        //     if (page >= lastPage - 1) {
                        //         $(this).prop('disabled', true);
                        //     }
                        // });
                        //
                        // iframe.find("#chartPaginationDiv").on('click', '#chartPrevBtn', function () {
                        //     var page = parseInt(iframe.find('#chartPaginationDiv').attr("page"));
                        //     lastPage = Math.floor(parseInt(iframe.find('#chartPaginationDiv').attr("lastidx")) / 50);
                        //     if (page <= lastPage) {
                        //         iframe.find('#chartPaginationDiv').find('#chartNextBtn').prop('disabled', false);
                        //     }
                        //     hide_rows(page, iframe);
                        //     page--;
                        //     show_rows(page, iframe);
                        //     iframe.find('#chartPaginationDiv').attr("page", page);
                        //     if (page <= 0) {
                        //         $(this).prop('disabled', true);
                        //     }
                        // });
                        //
                        // function hide_rows(page, iframe) {
                        //     for (ix = page * 50; ix < (page + 1) * 50; ix++) {
                        //         iframe.find('.table > tbody > tr[page="' + ix + '"]').hide();
                        //     }
                        // }
                        //
                        // function show_rows(page, iframe) {
                        //     for (ix = page * 50; ix < (page + 1) * 50; ix++) {
                        //         iframe.find('.table > tbody > tr[page="' + ix + '"]').show();
                        //     }
                        // }
                        init = 5;
                        tour = tour_guide_senario(tour,comp_type);
                    }
                    else{
                        $('#add_layer_btn').parent().hide();
                        $('#layers-list').parent().hide();
                        $('#myModal #submit-modal-btn').hide();
                    }
                });
            }

            $("#dismiss-modal-btn").click(function m(e) {
                refresh_visualisation_modal();
                $('#select_viz_popover').prop('disabled', true);
                $('#select_conf_popover').prop('disabled', true);
                // $('#myModal #viz_container').html('<div class="loadingFrame">' +
                //     '                    <img src="' + img_source_path + '"/>' +
                //     '                </div>');
            });

            $("#myModal #submit-modal-btn").click(function () {
                init =11;
                tour = tour_guide_senario(tour,'');
                if (vis_created_flag!==false){
                    refresh_visualisation_modal();
                }else{
                    alert('Please create a Visualisation first.')
                }
            });
            $("#myModal #submit-note-btn").click(function () {
                refresh_visualisation_modal();
            });

            function refresh_visualisation_modal(){
                open_modal = false;
                $('#layers-list ul').empty();
                $("#query_name_span").text(null);
                layer_count = 0;
                layer_json = [];
                selected_visualization = null;
                first_time = true ;
                vis_created_flag = false;
                contour_flag = false;
                $('#myModal #viz_config #add_layer_btn').parent().hide();
                $('#myModal #viz_config #layers-list').parent().hide();
                $("#viz_config .list-group").children().each(function () {
                    $(this).find("#selected_viz_span").hide();
                });
                $("#viz_config").find("ul").children().each(function (index) {
                        $(this).removeClass('disabled');
                });
                $('.viz_item').popover('hide');
                $('#myModal #viz_config .list-group').hide();
                $('#myModal #viz_config #viz_container').hide();


            }

            function check_list(list){
                flag = true;
                for(var i=0; i<list.length; i++){
                    if(list[i]===false){
                        flag=false;
                    }
                }
                return flag;
            }

            function limit_points(input, viz_conf, allow_submit, unit, parameter_id){
                if (input.val()>viz_conf['limit'] || input.val()<=0 || (input.val()==='')){
                        if(allow_submit[parameter_id]===true) {
                            $("<div class='conf-error-message limit_oob_message'>* Number of "+unit+" must be below " + String(viz_conf['limit']) + " and above 0.</div>").insertBefore("#select_conf_ok");
                            $('#select_conf_ok').addClass('disabled');
                        }
                        allow_submit[parameter_id] = false;
                    }else{
                        allow_submit[parameter_id] = true;
                        $('.limit_oob_message').remove();
                        if(check_list(allow_submit)) {
                            $('#select_conf_ok').removeClass('disabled');
                        }
                    }
                return allow_submit
            }


            function missing_parameter(col_select, allow_submit,parameter_name,parameter_id){
                if((col_select.val()=== null)||(col_select.val().length===0)){
                        if(allow_submit[parameter_id]===true) {
                            $('#select_conf_ok').addClass('disabled');
                            $("<div class='conf-error-message "+parameter_name+"_missing_error'>* Selection of "+ parameter_name +" is required.</div>").insertBefore("#select_conf_ok");
                        }
                        allow_submit[parameter_id] = false;
                    }
                    else{
                        allow_submit[parameter_id] = true;
                        $('.'+parameter_name+'_missing_error').remove();
                        if(check_list(allow_submit)){
                            $('#select_conf_ok').removeClass('disabled');
                        }
                    }
                return allow_submit
            }
            tour = tour_guide_senario('', '');
            $('#myModal').on('shown.bs.modal', function (e) {
                init = 1;
                tour = tour_guide_senario(tour, "");
            })

            function tour_guide_senario(tour, viz_type){
                // alert(init);
                if (init=== 0) {
                    var second_scenario_tour = new Tour({
                        storage: false,
                        template: "<div class='popover tour' style='max-width:400px; max-height: 160px; min-width: 250px; min-height: 100px; color: black;'>" +
                        "<div class='arrow'></div>" +
                        "<h3 class='popover-title' style='box-shadow: 0px 1px #bfbfbf;'></h3>" +
                        "<div class='popover-content'></div>" +
                        "<div class='popover-navigation'>" +
                        "<button class='btn btn-sm btn-primary' data-role='next'>Next »</button>" +
                        "<button class='btn btn-sm btn-primary pull-right' data-role='end'>End tour</button>" +
                        "</div>" +
                        "</div>",
                    });
                    second_scenario_tour.addStep({
                        element: "#new_widget_btn",
                        placement: "right",
                        title: "Widget Creation",
                        content: "Click the button to create a new visualisation or note.",
                    });

                    second_scenario_tour.init();
                    second_scenario_tour.start(true);
                    return second_scenario_tour;
                }else if(init===1){
                    tour.addStep({
                        element: "#tour_input_select_data",
                        placement: "right",
                        title: "Select Query",
                        content: "Select a Query to use for the creation of a visualisation.",
                        });
                    tour.next();
                    // init++;
                    return tour;
                }else if (init===2){
                    $('.tour').hide();
                    return tour;
                }else if (init===3){
                    tour.addStep({
                        element: ".list-group",
                        placement: "right",
                        title: "Select Visualisation",
                        content: "Select the proper Visualisation from the list, fill in the form and press OK.",
                        });
                    tour.next();
                    return tour;
                }else if (init===4){
                    $('.tour').hide();
                    return tour;
                }else if (init===5){
                    if(viz_type==='map'){
                        tour.addStep({
                            element: "#add_layer_btn",
                            placement: "left",
                            title: "Save Layer",
                            content: "Save the created map visualisation to a new layer and create a new one.",
                            });
                        tour.next();
                        return tour;
                    }
                    else{
                        tour.addStep({
                            element: "#submit-modal-btn",
                            placement: "left",
                            title: "Add visualisation to Dashboard.",
                            content: "Add the created visualisation to the Dashboard.",
                            });
                        tour.next();
                        return tour;
                    }
                }else if (init===6){
                    tour.addStep({
                        element: "#tour_input_select_data",
                        placement: "right",
                        title: "Select Query",
                        content: "Select another Query to use for the creation of another layer of the visualisation.",
                        });
                    tour.next();
                    return tour;
                }else if (init===7){
                    $('.tour').hide();
                    return tour;
                }else if (init===8){
                    tour.addStep({
                        element: ".list-group",
                        placement: "right",
                        title: "Select Visualisation",
                        content: "Select another map Visualisation to put on top of the existing map.",
                        });
                    tour.next();
                    return tour;
                }else if (init===9) {
                    $('.tour').hide();
                    return tour;
                }else if (init ===10){
                    tour.addStep({
                            element: "#submit-modal-btn",
                            placement: "left",
                            title: "Add visualisation to Dashboard.",
                            content: "Add the created multilayer visualisation to the Dashboard.",
                            });
                        tour.next();
                        return tour;
                }
                else if((init===11)){
                    tour.addStep({
                            element: "#dashboard_title",
                            placement: "right",
                            title: "Dashboard Title",
                            content: "Fill in the title of the Dashboard.",
                            });
                    tour.addStep({
                            element: "#privacy_status",
                            placement: "right",
                            title: "Permission Settings",
                            content: "Choose whether the dashboard is going to be private or public.",
                            });
                    tour.addStep({
                            element: "#save_dashboard_btn",
                            placement: "right",
                            title: "Save Dashboard",
                            content: "Save the created Dashboard.",
                            });
                        tour.next();
                        return tour;
                }
            }



        });


        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            }
        });