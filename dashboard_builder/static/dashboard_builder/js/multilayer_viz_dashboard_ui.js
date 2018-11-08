$("#select_data_popover").click(function () {
            $('.viz_item').popover('hide');
        });
        var new_query_id;
        // {#Variable to store active ckeditor version #}
        var textEditor = textEditor = CKEDITOR.appendTo('viz_note');
        // {#Function to change tabs in modal from data to notes and create new ckeditor instance if it doesnt exist#}
        $(document).ready(function () {
            var selected_val = null;
            var var_list = null;
            var var_select = null;
            var col_select = null;
            var flag = false;

            $('#submit-modal-btn').show();
            $('#layers-list ul').empty();
            $("#query_name_span").text(null);
            var layer_count = 0;
            var layer_json = [];
            var json;
            var selected_visualization = null;
            var first_time = true ;
            var vis_created_flag = false;
            $("#add_layer_btn").click(function () {
                if((new_query_id!=null)&&(selected_visualization!=null)) {
                    alert("Layer is now saved. Please add a new layer!");
                    $("#viz_config").find("ul").children().each(function (index) {
                        if ($(this).attr("data-viz-type") != "map") {
                            $(this).addClass('disabled');
                        }
                    });
                    $(".list-group").css('visibility','hidden');
                    $("#viz_config .list-group").children().each(function () {
                        $(this).find("#selected_viz_span").hide();
                    })
                    layer_json = [];
                    for (var i = 0; i < json.length; i++) {
                        var obj = json[i];
                        layer_json.push({});
                        for (var key in obj) {
                            layer_json[i][key] = obj[key];
                        }
                    }
                    $("#layers-list ul").append('<li class="layer_list_element" id='+String(layer_count)+' role=\"presentation\"><a class="col-10" style="display:inline;pointer-events:none;" role=\"menuitem\" tabindex=\"-1\" href=\"#\"> Query ID: ' + $("#query_name_span").text() + ' / Visualization: ' + String(selected_visualization) + '</a><button id=btn'+String(layer_count)+' style="display: inline; padding:2px 5px; font-size:10px;" type="button" class="btn btn-xs btn-primary col-2"><i class="glyphicon glyphicon-remove"></i></button></li>');
                    $(".layer_list_element #btn"+String(layer_count)).click(function () {
                         $("#viz_config .list-group").children().each(function () {
                                $(this).find("#selected_viz_span").hide();
                            })
                        var del_id = String(parseInt($(this).closest('li').attr('id')));
                        for (var i = 0; i < layer_json.length; i++) {
                            var obj = layer_json[i];
                            if (obj['layer_id']==del_id){
                                layer_count = layer_count-1;
                                layer_json.splice(i,1);
                                $(this).closest('li').remove();
                                for(var j = i ; j < layer_json.length; j++){
                                    $(".layer_list_element #btn"+String(j+1)).closest('li').attr('id',String(j));
                                    $(".layer_list_element #btn"+String(j+1)).attr('id','btn'+String(j));
                                    obj = layer_json[j];
                                    layer_json[j]['layer_id'] = layer_json[j]['layer_id']-1;
                                }
                                i=j;
                            }
                        }
                        mapVizUrlCreator(layer_json,layer_count);
                    })
                    layer_count = layer_count+1;
                }
                else{
                    alert("Please select data and add visualization!")
                }
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
                $('#submit-modal-btn').show();
            });
            $("#myModal #select_data_popover").popover({
                html: true,
                animation: true,
                title: 'Select query to use',
                content: function () {
                    return $('#query-container').html();
                }
            }).click(function (e) {
                $(this).popover('toggle');
                $('.popover-content .form-group #query-select').dropdown();

                $('.popover-content #query-select').on('change', function () {
                    new_query_id = $(this).children(":selected").attr("id");
                    var new_query_doc = $('#new_query_doc').val();
                    $('#myModal #selected_query').val(new_query_id);
                    updateVariables(this);
                });
                $('.popover-content #select_data_ok').click(function (e) {
                    $('#query_name_span').show();
                    $('#query_name_span').text(new_query_id);
                    $('#myModal #select_data_popover').popover("hide");
                    $('#viz_config').show();
                    $(".list-group").css('visibility','visible');
                })
                $('.popover-content #select_data_cancel').click(function (e) {
                    $('#myModal #select_data_popover').popover("hide");
                })
            });
            $(".viz_item").click(function (element) {
                $('.popover').hide();
                var component_id = $(this).attr('data-viz-id');
                var component_type = $(this).attr('data-viz-type');
                var component_selector = 'li[data-viz-id="' + component_id + '"]';
                $(component_selector).popover({
                    html: true,
                    title: 'Configure visualisation',
                    trigger:'manual',
                    content: function () {
                        return $('.all_viz_forms  #viz_' + String(component_id)).clone();
                    }
                });

                updateVariables($('#query-select'));

                $(component_selector).popover('show');
                $(component_selector).on("hidden.bs.popover", function(e) {
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
                $(popver_id + ' #select_conf_ok').click(function (e) {
                    selected_visualization = $(component_selector).text();
                    $("#viz_config .list-group").children().each(function () {
                        $(this).find("#selected_viz_span").hide();
                    })
                    $(component_selector).find("#selected_viz_span").show();
                    if (component_type == 'map') {
                        $('#add_layer_btn').show();
                        $('#layers-list').show();
                        $('#layers-list').css("display", "inline");
                    }
                    else {
                        $('#add_layer_btn').hide();
                        $('#layers-list').hide();
                    }
                    submit_conf(component_selector, component_type);
                    $(component_selector).popover("hide");
                });
                $(popver_id + ' #select_conf_cancel').click(function (e) {
                    $(component_selector).popover("hide");
                });
            });

            function updateVariables(element){
                $('#myModal .variable-select').find('option').remove();
                $('#myModal .variables-select ').find('option').remove();
                $('#myModal .column-select ').find('option').remove();
                $('#myModal .columns-select ').find('option').remove();
                $('#myModal .ais-select ').find('option').remove();
                var variables_content = $('#query-variables-select-container #'+String(new_query_id)).html();
                var dimensions_content = $('#query-dimensions-select-container #'+String(new_query_id)).html();
                var dataset_arguments_content = $('#query-datasets-extra-arguments #'+String(new_query_id)).html();
                $('#myModal .variable-select ').html(variables_content);
                $('#myModal .variables-select ').html(variables_content);
                $('#myModal .column-select ').html(variables_content + dimensions_content);
                $('#myModal .columns-select ').html(variables_content + dimensions_content);
                $("#myModal .dataset-argument-select").html(dataset_arguments_content);
            }
            function populate_selects(){

                $('#use_existing_temp_res').parent().checkbox().first().checkbox({
                    onChecked: function(){
                        $('#temporal_resolution').parent().addClass('disabled');
                    },
                    onUnchecked: function () {
                        $('#temporal_resolution').parent().removeClass('disabled');
                    }
                });

                $('.checkbox').parent().removeClass('form-group label-floating');

                $('#select_all_columns').parent().checkbox().first().checkbox({
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

            function submit_conf(component_selector,component_type) {
                var conf_popover_id;
                var submitted_args;
                var selects;
                var myData;
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
                    viz_request += '?';
                    viz_request += myData;
                    viz_request += '&query=' + $('#myModal #selected_query').val();
                    show_viz(viz_request);
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
                        mapVizUrlCreator(json, layer_count + 1);
                    }
                    else{
                        first_time = false;
                        mapVizUrlCreator(json, layer_count);
                    }
                };
                vis_created_flag = true;

            };
            function mapVizUrlCreator(json,my_layer_count){
                var viz_request = "/visualizations/get_map_visualization/?";
                viz_request += "layer_count="+String(my_layer_count)+"&";
                var url="";
                for (var i = 0; i < json.length; i++) {
                    var obj =json[i];
                    for (var key in obj) {
                        url = url + "&" + (key)+obj['layer_id'] + "=" + (obj[key]);
                    }
                }
                url = url.replace("&","");
                viz_request += url;
                show_viz(viz_request);
            }
            function getFormData(form,count,query){
                var unindexed_array = form.serializeArray();
                var indexed_array = {};
                $.map(unindexed_array, function(n, i){
                    indexed_array[n['name']] = n['value'];
                });
                indexed_array['query'] = query;
                indexed_array['layer_id'] = String(count);
                indexed_array['cached_file_id'] = String(Math.floor(Date.now() / 1000))+'layer'+String(count) ;
                return indexed_array;
            }
            function show_viz(viz_request) {
                $("#viz_container").html('<div class="loadingFrame"><img src="' + img_source_path + '"/></div><iframe class="iframe-class" id="viz-iframe" ' +
                    'src="' + viz_request + '" frameborder="0" allowfullscreen="" ' +
                    '></iframe>');
                $('#myModal #submit-modal-btn').show();
                $("#myModal #viz_container .loadingFrame").css( "display", "block" );
                $("#myModal #viz_container iframe").on( "load", function(){
                    $(this).siblings(".loadingFrame").css( "display", "none" );
                });
            }
            $("#dismiss-modal-btn").click(function m(e) {
                refresh_visualisation_modal();
                $('#select_viz_popover').prop('disabled', true);
                $('#select_conf_popover').prop('disabled', true);
                $('#myModal #viz_container').html('<div class="loadingFrame">' +
                    '                    <img src="' + img_source_path + '"/>' +
                    '                </div>');
            });

            $("#myModal #submit-modal-btn").click(function () {
                if (vis_created_flag!=false){
                refresh_visualisation_modal();
                }else{
                    alert('Please create a Visualisation first.')
                }
            });
            $("#myModal #submit-note-btn").click(function () {
                refresh_visualisation_modal();
            });

            function refresh_visualisation_modal(){
                $('#layers-list ul').empty();
                $("#query_name_span").text(null);
                layer_count = 0;
                layer_json = [];
                selected_visualization = null;
                first_time = true ;
                vis_created_flag = false;
                $('#add_layer_btn').hide();
                $('#layers-list').hide();
                $("#viz_config .list-group").children().each(function () {
                    $(this).find("#selected_viz_span").hide();
                });
                $("#viz_config").find("ul").children().each(function (index) {
                        $(this).removeClass('disabled');
                });
                $('.viz_item').popover('hide');
                $('#myModal #viz_config').hide();

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
                var plotline_vessel_course_input = $('.popover-content #viz_'+plotline_vessel_course_id+' #m_limit');
                plotline_vessel_course_input.val(0);
                plotline_vessel_course_input.on('input',function () {
                    if (plotline_vessel_course_input.val()>=100 || plotline_vessel_course_input.val()<0){
                        alert('Please set the limit below 100 and above 0.');
                        plotline_vessel_course_input.val(0);
                    }
                });
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