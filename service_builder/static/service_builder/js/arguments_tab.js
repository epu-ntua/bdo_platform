$(document).ready(function(){
    var countrow=0;
    var available_filter_args;
    $("#argument-select-container").hide();
    $("#argument-newvar-form-container").hide();

    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })

    $("#add_alg_arg_popbtn").popover({
        html: true,
        animation:true,
        trigger: 'manual',
        content: function() {
            return $('#argument-newvar-form-container').html();
        }
    }).click(function(e) {
        $('.btn_pop').not(this).popover('hide');
        $(this).popover('toggle');
        $("#select_option_clear").on('click',function(){
            $("#alg_select_options").val('{"options":[]}');
            $("#alg_select_options_sel").empty();

        });
        $("#alg_select_options").val('{"options":[]}')
        populate_select("#alg_vartype");
        $('.popover-content #alg_vartype').on('change', function() {
            selected = true;
            var new_type = $("#alg_vartype option:selected").val();
            if(new_type == 'SELECT') {
                $("#alg_select_options").prop('disabled', true);
                $("#alg_vardefault").val('');
                $("#hidden_select_options").show();
                $("#arg_def_val_div").hide();
                $("#select_option_button").on('click',function(){
                    var sel_val = $("#select_value_input").val();
                    var sel_text = $("#select_text_input").val();
                    var txt_area_new =select_json_creator(sel_val,sel_text,$("#alg_select_options"))
                    $("#alg_select_options").val(txt_area_new)
                    $("#select_value_input").val('');
                    $("#select_text_input").val('');
                    populate_option_select_json($("#alg_select_options_sel"),$("#alg_select_options").val());

                })
            }
            else{
                $("#alg_select_options").val('{"options":[]}')
                $("#hidden_select_options").hide();
                $("#arg_def_val_div").show();
            }

         });

        $("#alg_select_options_sel").empty();
        $('.popover-content #alg_vartype').select2();

        var new_alg_arg_name;
        var new_alg_arg_title ;
        var new_alg_arg_type;
        var new_alg_arg_typevalue;
        var new_alg_arg_select_options;
        var new_alg_arg_default;
        var new_alg_arg_desc;
        $('.popover-content #add_new_argument_btn2').click(function (e) {
            countrow=countrow+1;
            new_alg_arg_name = $("#alg_varname").val();
            new_alg_arg_title = $("#alg_vartitle").val();
            if(check_duplicate_title_name(new_alg_arg_name,new_alg_arg_title,"")){
                alert("Argument name or title already exists!")
            }
            else if ((new_alg_arg_name!=null)&&(new_alg_arg_title!=null)&&(new_alg_arg_name.trim() !="")&&(new_alg_arg_title.trim()!="")){
                var edit_btn_id="edit_btn_id_" + countrow.toString();
                var del_btn_id="del_btn_id_"+ countrow.toString();
                var del_row_btn='<button type="button" id="'+del_btn_id+'"class="btn btn-primary btn-xs a-btn-slide-text">' +
                    ' <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>' +
                    '</button>';
                var edit_row_btn='<button type="button" id="'+edit_btn_id+'"class="btn btn-primary btn-xs a-btn-slide-text btn_pop">' +
                    ' <span class="glyphicon glyphicon-edit" aria-hidden="true"></span>' +
                    ' </button>';

                var edit_sel="#"+edit_btn_id;
                var del_sel="#"+del_btn_id;

                // new_alg_arg_type = $("select#alg_vartype option:checked").val();
                new_alg_arg_type = $("select#alg_vartype option:checked").text();
                new_alg_arg_typevalue=$("#alg_vartype").val();
                if (new_alg_arg_typevalue == 'SELECT') {
                    new_alg_arg_select_options = $("#alg_select_options").val();
                }
                new_alg_arg_default=$("#alg_vardefault").val();
                new_alg_arg_desc = $("#alg_vardescr").val();
                var new_arg_tr_string = "<tr id='row_id_"+countrow.toString()+"'> <td data-columnname='name'>" + new_alg_arg_name + "</td> <td data-columnname='title'>" + new_alg_arg_title + "</td> <td data-columnname='type'><span> " + new_alg_arg_type + "</span><span style='display:none;'>"+new_alg_arg_typevalue+"</span> <span style='display:none;'>"+new_alg_arg_select_options+"</span> </td> <td data-columnname='default'>" + new_alg_arg_default + "</td> <td data-columnname='description'> <div style='min-width: 100%'>" + new_alg_arg_desc + " </div> </td> <td>"+ edit_row_btn +del_row_btn +" </td> </tr>";
                $('#selected-arguments-table2 tbody').append(new_arg_tr_string);

                $(edit_sel).popover({
                    html: true,
                    animation:true,
                    trigger: 'manual',
                    placement: 'left',
                    content: function() {
                        return $('#argument-newvar-form-container').html();
                    }
                }).click(function(e) {
                    $('.btn_pop').not(this).popover('hide');
                    $(this).popover('toggle');
                    $("#select_option_clear").on('click',function(){
                        $("#alg_select_options").val('{"options":[]}');
                        $("#alg_select_options_sel").empty();

                    });

                    populate_select("#alg_vartype");
                    $('.popover-content #alg_vartype').on('change', function() {
                        selected = true;
                        var new_type = $("#alg_vartype option:selected").val();
                        if(new_type == 'SELECT') {
                            $("#alg_vardefault").val('');
                            $("#hidden_select_options").show();
                            $("#arg_def_val_div").hide();
                            $("#select_option_button").on('click',function(){
                                var sel_val = $("#select_value_input").val();
                                var sel_text = $("#select_text_input").val();
                                var txt_area_new =select_json_creator(sel_val,sel_text,$("#alg_select_options"))
                                $("#alg_select_options").val(txt_area_new)
                                $("#select_value_input").val('');
                                $("#select_text_input").val('');
                                populate_option_select_json($("#alg_select_options_sel"),$("#alg_select_options").val());

                            })
                        }
                        else{
                            $("#alg_select_options").val('{"options":[]}')
                            $("#hidden_select_options").hide();
                            $("#arg_def_val_div").show();

                        }
                    });


                    $('.popover-content #alg_vartype').select2();

                    var temp="#"+$(this).attr('id');
                    temp=temp.replace("#edit_btn_id_","");
                    temp="#row_id_"+temp;

                    var temp_alg_arg_name=$(temp).find($("td[data-columnname='name']")).text().trim();
                    var temp_alg_arg_title=$(temp).find($("td[data-columnname='title']")).text().trim();
                    var temp_alg_arg_type=$(temp).find($("td[data-columnname='type']")).children().eq(0).text().trim();
                    var temp_alg_arg_typevalue=$(temp).find($("td[data-columnname='type']")).children().eq(1).text().trim();
                    var temp_alg_arg_select_options=$(temp).find($("td[data-columnname='type']")).children().eq(2).text().trim();
                    var temp_alg_arg_default=$(temp).find($("td[data-columnname='default']")).text().trim();
                    var temp_alg_arg_desc=$(temp).find($("td[data-columnname='description']")).text().trim();


                    $("#alg_varname").val(temp_alg_arg_name);
                    $("#alg_vartitle").val(temp_alg_arg_title);
                    $("select#alg_vartype").val((temp_alg_arg_typevalue).trim()).change();
                    $("#alg_select_options").text(temp_alg_arg_select_options);
                    populate_option_select_json($("#alg_select_options_sel"),$("#alg_select_options").val());
                    $("#alg_vardefault").val(temp_alg_arg_default);
                    $("#alg_vardescr").text(temp_alg_arg_desc);


                    // alert(new_alg_arg_name+" "+new_alg_arg_title+" "+new_alg_arg_type+" "+new_alg_arg_desc);
                    $('.popover-content #add_new_argument_btn2').click(function (e) {
                        new_alg_arg_name = $("#alg_varname").val();
                        new_alg_arg_title = $("#alg_vartitle").val();
                        new_alg_arg_type = $("select#alg_vartype option:checked").text();
                        new_alg_arg_typevalue=$("#alg_vartype").val();
                        new_alg_arg_select_options=$("#alg_select_options").val();
                        new_alg_arg_default = $("#alg_vardefault").val();
                        new_alg_arg_desc = $("#alg_vardescr").val();
                        if(check_duplicate_title_name(new_alg_arg_name,new_alg_arg_title,temp.replace("#",""))){
                            alert("Argument name or title already exists!")
                        }
                        else if ((new_alg_arg_name!=null)&&(new_alg_arg_title!=null)&&(new_alg_arg_name.trim() !="")&&(new_alg_arg_title.trim()!="")){
                            $(temp).find($("td[data-columnname='name']")).text(new_alg_arg_name);
                            $(temp).find($("td[data-columnname='title']")).text(new_alg_arg_title);
                            $(temp).find($("td[data-columnname='type']")).children().eq(0).text(new_alg_arg_type);
                            $(temp).find($("td[data-columnname='type']")).children().eq(1).text(new_alg_arg_typevalue);
                            $(temp).find($("td[data-columnname='type']")).children().eq(2).text(new_alg_arg_select_options);
                            $(temp).find($("td[data-columnname='default']")).text(new_alg_arg_default);
                            $(temp).find($("td[data-columnname='description']")).text(new_alg_arg_desc);
                            // Update service arguments on backend
                            update_service_arguments('alg');
                            $(edit_sel).popover("hide");
                        }else{
                            alert("Please fill the name and title of the new variable!")
                        }
                    });

                });
                $(del_sel).click(function () {
                    var temp="#"+$(this).attr('id');
                    temp=temp.replace("#del_btn_id_","");
                    temp="#row_id_"+temp;
                    $(temp).remove();
                    // Update service arguments on backend
                    update_service_arguments('alg');
                });
                // Update service arguments on backend
                update_service_arguments('alg');
                //Update backend when the service is published.
                $('#add_alg_arg_popbtn').popover("hide");
            }else{
                alert("Please fill the name and title of the new variable!")
            }
        });

    });





    $("#add_filter_arg_popbtn").popover({
        html: true,
        animation:true,
        trigger: 'manual',
        content: function() {
            return $('#argument-select-container').html();
        }
    }).click(function(e) {
        $('.btn_pop').not(this).popover('hide');
        $(this).popover('toggle');

        populate_select("#filter_type");

        $('.popover-content #filter_type').select2();


        available_filter_args = JSON.parse('{}');
        $('#selected-queries-table tbody tr').each(function( index ) {
            console.log( index + ": " + $( this ).find($("td[data-columnname='doc']")).text());
            console.log( index + ": " + $( this ).find($("td[data-columnname='doc']")).text().replace(/"'/g , "'").replace(/'"/g , "'").replace(/u'/g , "'").replace(/u"/g , "'").replace(/'/g , '"').replace(/False/g , '"False"').replace(/True/g , '"True"'));
            console.log( index + ": " + JSON.stringify(JSON.parse($( this ).find($("td[data-columnname='doc']")).text().replace(/"'/g , "'").replace(/'"/g , "'").replace(/u'/g , "'").replace(/u"/g , "'").replace(/'/g , '"').replace(/False/g , '"False"').replace(/True/g , '"True"').replace(/None/g , '"None"'))['filters']) );
            var query_doc = JSON.parse($( this ).find($("td[data-columnname='doc']")).text().replace(/"'/g , "'").replace(/'"/g , "'").replace(/u'/g , "'").replace(/u"/g , "'").replace(/'/g , '"').replace(/False/g , '"False"').replace(/True/g , '"True"').replace(/None/g , '"None"'));
            var filters = query_doc['filters'];
            if (filters != undefined){
                parse_filters($( this ).find($("td[data-columnname='query_id']")).text(), $( this ).find($("td[data-columnname='number']")).text(), filters) ;
            }
        });


        $('#query-argument-select').empty();
        $('#query-argument-select').append('<option disabled selected value="">-- select one of the available filters --</option>');
        // var keys = [];
        // for(var k in available_filter_args) keys.push(k);
        for(var query in available_filter_args){
            console.log(query);
            for(var arg_idx in available_filter_args[query]['filter_args']) {
                var display_name = available_filter_args[query]['display_name'];
                var arg = available_filter_args[query]['filter_args'][arg_idx];
                var arg_a = arg['a'].split(/_(.+)/)[1];
                var arg_op = arg['op'];
                var arg_b = arg['b'];
                var text_in_option = display_name + '-' + arg_a +' '+ arg_op +' '+ arg_b;
                if (arg_op === 'inside_rect'){
                    text_in_option =
                        display_name + ' - ' +
                        'Latitude between ' +
                        '(' + String(arg_b).split('<<')[1].split(',')[0] + ', ' + String(arg_b).split('>,<')[1].split(',')[0] + ')' +
                        ' and Longitude between ' +
                        '(' + String(arg_b).split(',')[1].split('>')[0] + ', ' + String(arg_b).split('>,<')[1].split(',')[1].split('>>')[0] + ')' +
                        ' degrees';
                }
                if (arg_op === 'gt'){
                    text_in_option = display_name + ' - ' + arg_a +' '+ '>' +' '+ arg_b;
                }
                if (arg_op === 'gte'){
                    text_in_option = display_name + ' - ' + arg_a +' '+ '>=' +' '+ arg_b;
                }
                if (arg_op === 'lt'){
                    text_in_option = display_name + ' - ' + arg_a +' '+ '<' +' '+ arg_b;
                }
                if (arg_op === 'lte'){
                    text_in_option = display_name + ' - ' + arg_a +' '+ '<=' +' '+ arg_b;
                }
                if (arg_op === 'eq'){
                    text_in_option = display_name + ' - ' + arg_a +' '+ '=' +' '+ arg_b;
                }
                if (arg_op === 'nqe'){
                    text_in_option = display_name + ' - ' + arg_a +' '+ '<>' +' '+ arg_b;
                }
                if (arg_op === 'gt_time'){
                    text_in_option = display_name + ' - ' + arg_a +' '+ '>' +' '+ arg_b;
                }
                if (arg_op === 'gte_time'){
                    text_in_option = display_name + ' - ' + arg_a +' '+ '>=' +' '+ arg_b;
                }
                if (arg_op === 'lt_time'){
                    text_in_option = display_name + ' - ' + arg_a +' '+ '<' +' '+ arg_b;
                }
                if (arg_op === 'lte_time'){
                    text_in_option = display_name + ' - ' + arg_a +' '+ '<=' +' '+ arg_b;
                }
                $('#query-argument-select').append('<option  data-query-id="'+query+'" data-display_name="'+display_name+'" data-arg-a="'+arg_a+'" data-arg-op="'+arg_op+'" data-arg-b="'+arg_b+'" title="' + text_in_option + '"> ' + text_in_option + ' </option>');
            }
        }

        $('.popover-content #query-argument-select').select2();

        var new_arg_query_id;
        var new_arg_query_display_name;
        var new_arg_a;
        var new_arg_op;
        var new_arg_b;
        var selected = false;
        $('.popover-content #query-argument-select').on('change', function() {
            selected = true;
            new_arg_query_id = $(this).children(":selected").attr("data-query-id");
            new_arg_query_display_name = $(this).children(":selected").attr("data-display_name");
            new_arg_a = $(this).children(":selected").attr("data-arg-a");
            new_arg_op = $(this).children(":selected").attr("data-arg-op");
            new_arg_b = $(this).children(":selected").attr("data-arg-b");
            $('.popover-content #filter_def_val').val(new_arg_b).attr('disabled','disabled');
            // alert(new_arg_op);
            if (new_arg_op === 'inside_rect'){
                $("#filter_type option").not('[value="SPATIAL_COV"]').attr('disabled',true);
                $("#filter_type").find('option[value="SPATIAL_COV"]').attr("disabled", false);
                $("#filter_type").val('SPATIAL_COV').trigger('change');
                $("#filter_type").select2();
            }
            else if ((arg_op === 'gt_time') || (arg_op === 'gte_time') || (arg_op === 'lt_time') || (arg_op === 'lte_time')){
                $("#filter_type option").not('[value="DATETIME"]').attr('disabled',true);
                $("#filter_type").find('option[value="DATETIME"]').attr("disabled", false);
                $("#filter_type").val('DATETIME').trigger('change');
                $("#filter_type").select2();
            }
            else{
                $("#filter_type option").attr("disabled", false);
                $("#filter_type").find('option[value="SPATIAL_COV"]').attr('disabled',true);
                $("#filter_type").find('option[value="DATETIME"]').attr('disabled',true);
                $("#filter_type").val('FLOAT').trigger('change');
                $("#filter_type").select2();
            }
        });


        $('.popover-content #add_new_argument_btn1').click(function (e) {
            countrow=countrow+1;
            var new_filter_arg_name = $(".popover-content #filter_varname").val();
            var new_filter_arg_title = $(".popover-content #filter_vartitle").val();
            var new_filter_arg_def = $(" .popover-content #filter_def_val").val();
            var new_filter_arg_desc = $(".popover-content #filter_descr").val();
            var new_filter_arg_type = $("select#filter_type option:checked").text();
            var new_filter_arg_typevalue = $("#filter_type").val();
            var edit_btn_id="edit_btn_id_" + countrow.toString();
            var del_btn_id="del_btn_id_"+ countrow.toString();
            var del_row_btn='<button id="' + del_btn_id +'" class="btn btn-primary btn-xs a-btn-slide-text">' +
                ' <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>' +
                '</button>';
            var edit_row_btn='<button id="'+ edit_btn_id+'" class="btn btn-primary btn-xs a-btn-slide-text btn_pop">' +
                ' <span class="glyphicon glyphicon-edit" aria-hidden="true"></span>' +
                ' </button>';
            var edit_sel="#"+edit_btn_id;
            var del_sel="#"+del_btn_id;
            if(check_duplicate_title_name(new_filter_arg_name,new_filter_arg_title,"")){
                alert("Argument name or title already exists!")
            }
            else if((selected)&&(new_filter_arg_title!=null)&&(new_filter_arg_def!=null)&&(new_filter_arg_title.trim()!="")&&(new_filter_arg_def.trim()!="")) {
                // var new_arg_tr_string = "<tr id='row_id_"+countrow.toString()+"'> <td data-columnname='query_id'>" + new_arg_query_id + "</td> <td data-columnname='query_name'>" + new_arg_query_display_name + "</td> <td data-columnname='filter'> <span>" + new_arg_a + " </span><span> " + new_arg_op + "</span></td> <td data-columnname='filter_type'> <span>"+ new_filter_arg_type+"</span><span style='display:none;'>"+new_filter_arg_typevalue+"</span>  </td><td data-columnname='def_val'> " +new_filter_arg_def + "</td> <td  data-columnname='name'>"+ new_filter_arg_name+"</td><td data-columnname='title'> " + new_filter_arg_title + "</td> <td data-columnname='description'><div  style='min-width: 100%'>" + new_filter_arg_desc + "</div></td><td>" + edit_row_btn +del_row_btn+"</td> </tr>";
                var new_arg_tr_string = "<tr id='row_id_"+countrow.toString()+"'> <td data-columnname='query_id' style='display: none;'>" + new_arg_query_id + "</td> <td data-columnname='query_name'>" + new_arg_query_display_name + "</td> <td data-columnname='filter'> <span>" + new_arg_a + " </span><span> " + new_arg_op + "</span></td> <td data-columnname='filter_type'> <span>"+ new_filter_arg_type+"</span><span style='display:none;'>"+new_filter_arg_typevalue+"</span>  </td><td data-columnname='def_val'> " +new_filter_arg_def + "</td> <td  data-columnname='name'>"+ new_filter_arg_name+"</td><td data-columnname='title'> " + new_filter_arg_title + "</td> <td data-columnname='description'><div  style='min-width: 100%'>" + new_filter_arg_desc + "</div></td><td>" + edit_row_btn +del_row_btn+"</td> </tr>";
                $('#selected-arguments-table1 tbody').append(new_arg_tr_string);

                $(edit_sel).popover({
                    html: true,
                    animation:true,
                    trigger: 'manual',
                    placement: 'left',
                    content: function() {
                        return $('#argument-select-container').html();
                    }
                }).click(function(e) {
                    $('.btn_pop').not(this).popover('hide');
                    $(this).popover('toggle');

                    populate_select("#filter_type");

                    $('.popover-content #filter_type').select2();

                    $('.popover-content #query-argument-select').remove();

                    var temp="#"+$(this).attr('id');
                    temp=temp.replace("#edit_btn_id_","");
                    temp="#row_id_"+temp;


                    var temp_filter_def_val=$(temp).find($("td[data-columnname='def_val']")).text();
                    var temp_filter_var_name=$(temp).find($("td[data-columnname='name']")).text();
                    var temp_filter_var_title=$(temp).find($("td[data-columnname='title']")).text();
                    var temp_filter_descr=$(temp).find($("td[data-columnname='description']")).text();
                    var temp_filter_type=$(temp).find($("td[data-columnname='filter_type']")).children().eq(0).text();
                    var temp_filter_typevalue=$(temp).find($("td[data-columnname='filter_type']")).children().eq(1).text();


                    // $("select#select2-query-argument-select-container ").val(temp_query_choice).change();

                    $("#filter_def_val").val(temp_filter_def_val);
                    $("#filter_varname").val(temp_filter_var_name);
                    $("#filter_vartitle").val(temp_filter_var_title);
                    $("#filter_descr").val(temp_filter_descr);
                    $("select#filter_type").val(temp_filter_typevalue.trim()).change();


                    // alert(new_alg_arg_name+" "+new_alg_arg_title+" "+new_alg_arg_type+" "+new_alg_arg_desc);
                    $('.popover-content #add_new_argument_btn1').click(function (e) {
                        var new_filter_def_val = $("#filter_def_val").val();
                        var new_filter_varname = $("#filter_varname").val();
                        var new_filter_vartitle = $("#filter_vartitle").val();
                        var new_filter_descr =  $("#filter_descr").val();
                        var new_filter_type = $("select#filter_type option:checked").text();
                        var new_filter_typevalue = $('#filter_type').val();

                         if(check_duplicate_title_name(new_filter_varname,new_filter_vartitle,temp.replace("#",""))){
                            alert("Argument name or title already exists!")
                         }
                         else if((new_filter_arg_title!=null)&&(new_filter_arg_def!=null)&&(new_filter_arg_title.trim()!="")&&(new_filter_arg_def.trim()!="")) {
                            $(temp).find($("td[data-columnname='def_val']")).text(new_filter_def_val);
                            $(temp).find($("td[data-columnname='name']")).text(new_filter_varname);
                            $(temp).find($("td[data-columnname='title']")).text(new_filter_vartitle);
                            $(temp).find($("td[data-columnname='description']")).text(new_filter_descr);
                            $(temp).find($("td[data-columnname='filter_type']")).children().eq(0).text(new_filter_type);
                            $(temp).find($("td[data-columnname='filter_type']")).children().eq(1).text(new_filter_typevalue);

                            // Update service arguments on backend
                            update_service_arguments('filter');
                            $(edit_sel).popover("hide");
                         }else{
                            alert("Please fill the name and title of the new variable!")
                        }
                    });

                });
                $(del_sel).click(function () {
                    var temp="#"+$(this).attr('id');
                    temp=temp.replace("#del_btn_id_","");
                    temp="#row_id_"+temp;
                    $(temp).remove();
                    // Update service arguments on backend
                    update_service_arguments('filter');
                });
                // Update service arguments on backend
                update_service_arguments('filter');
                //Chose to update arguments on backend (create JSON file) when publishing.
                selected = false;
                $('#add_filter_arg_popbtn').popover("hide");
            }
            else {
                alert("Please fill the necessary fields.")
            }

        })

    });



    function parse_filters(query_id, query_num, json){
        if(json['a'] != undefined) {
            if (json['a']['a'] == undefined) {
                if (available_filter_args[query_id] == undefined) {
                    available_filter_args[query_id] = {};
                    available_filter_args[query_id]['display_name'] = null;
                    available_filter_args[query_id]['filter_args'] = [];
                    console.log(JSON.stringify(available_filter_args));
                }
                console.log(JSON.stringify(available_filter_args));
                available_filter_args[query_id]['display_name'] = query_num;
                available_filter_args[query_id]['filter_args'].push(json);
            }
            else {
                parse_filters(query_id, query_num, json['a']);
                parse_filters(query_id, query_num, json['b']);
            }
        }
    }



    function populate_select(selector){
        $(selector).empty();
        $(selector).append('<option disabled selected value="">-- Select argument type --</option>');
        $(selector).append('<option value="INT">Integer</option>');
        $(selector).append('<option value="FLOAT">Float</option>');
        // $(selector).append('<option value="STRING">String</option>');
        $(selector).append('<option value="DATETIME">Date</option>');
        $(selector).append('<option value="SPATIAL_COV">Spatial Coverage</option>');
        // $(selector).append('<option value="SELECT">Select</option>');

    }

    function populate_option_select_json(selector,json_values){
        $(selector).empty();
        var obj = JSON.parse(json_values);
        length = obj.options.length;
        for (i = 0; i < length; i++){
            $(selector).append('<option value='+ JSON.stringify(obj.options[i]["val"]).split('"').join('')+'>Value: ' + JSON.stringify(obj.options[i]["val"]).split('"').join('') + ' - Text: ' + JSON.stringify(obj.options[i]["text"]).split('"').join('') + '</option>');
        }
        selector.select2();
    }

    function select_json_creator(val,text,selector){
        string = '{"value":"'+val.toString()+'","text":"'+text.toString()+'"}'
        json_obj_list= JSON.parse(selector.val());
        json = JSON.parse(string);
        json_obj_list['options'].push(json);
        return JSON.stringify(json_obj_list);



    }



    function check_duplicate_title_name(arg_name,arg_title,edit_row_id){
        var flag=false;
        $("#selected-arguments-table1 tbody tr").each(
            function(index, elem) {
                if((arg_name.trim()=== $(this).find($("td[data-columnname='name']")).text().trim())||(arg_title.trim()=== $(this).find($("td[data-columnname='title']")).text().trim())) {
                    if((edit_row_id=="")||(edit_row_id!=$(this).attr('id').trim())){
                        flag = true;
                    }
                }
            }
            );
        $("#selected-arguments-table2 tbody tr").each(
            function(index, elem) {
                if((arg_name.trim()=== $(this).find($("td[data-columnname='name']")).text().trim())||(arg_title.trim()=== $(this).find($("td[data-columnname='title']")).text().trim())) {
                    if((edit_row_id=="")||(edit_row_id!=$(this).attr('id').trim())){
                        flag = true;
                    }
                }
            }
        );
        return flag;
    };


});


