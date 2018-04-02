$(document).ready(function(){
    var available_filter_args;

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

    $("#add_argument_popbtn").popover({
        html: true,
        animation:true,
        trigger: 'manual',
        content: function() {
            return $('#argument-select-container').html();
        }
    }).click(function(e) {
        $(this).popover('toggle');


        available_filter_args = JSON.parse('{}');
        $('#selected-queries-table tbody tr').each(function( index ) {
            console.log( index + ": " + $( this ).children().eq(3).text());
            console.log( index + ": " + $( this ).children().eq(3).text().replace(/"'/g , "'").replace(/'"/g , "'").replace(/u'/g , "'").replace(/u"/g , "'").replace(/'/g , '"').replace(/False/g , '"False"').replace(/True/g , '"True"'));
            console.log( index + ": " + JSON.stringify(JSON.parse($( this ).children().eq(3).text().replace(/"'/g , "'").replace(/'"/g , "'").replace(/u'/g , "'").replace(/u"/g , "'").replace(/'/g , '"').replace(/False/g , '"False"').replace(/True/g , '"True"'))['filters']) );
            var query_doc = JSON.parse($( this ).children().eq(3).text().replace(/"'/g , "'").replace(/'"/g , "'").replace(/u'/g , "'").replace(/u"/g , "'").replace(/'/g , '"').replace(/False/g , '"False"').replace(/True/g , '"True"'));
            var filters = query_doc['filters'];
            if (filters != undefined){
                parse_filters($( this ).children().eq(0).text(), $( this ).children().eq(1).text(), filters) ;
            }
        });

        $('#query-argument-select').empty();
        $('#query-argument-select').append('<option disabled selected>-- select one of the available filters --</option>');
        // var keys = [];
        // for(var k in available_filter_args) keys.push(k);
        for(var query in available_filter_args){
            console.log(query);
            for(var arg_idx in available_filter_args[query]['filter_args']) {
                var display_name = available_filter_args[query]['display_name'];
                var arg = available_filter_args[query]['filter_args'][arg_idx];
                var arg_a = arg['a'];
                var arg_op = arg['op'];
                var arg_b = arg['b'];
                $('#query-argument-select').append('<option  data-query-id="'+query+'" data-display_name="'+display_name+'" data-arg-a="'+arg_a+'" data-arg-op="'+arg_op+'" data-arg-b="'+arg_b+'" title="' + display_name + '-' + arg_a +' '+ arg_op +' '+ arg_b + '"> ' + display_name + '-' + arg_a +' '+ arg_op +' '+ arg_b + ' </option>');
            }
        }
        $('.popover-content #query-argument-select').select2();
        // available_filter_args.forEach(function(value) {
        //   console.log(value);
        //   $('#query-argument-select').append('<option  value="'+value+'" title="'+value+'"> '+value+' </option>');
        // });

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
        });




        $('.popover-content #add_new_argument_btn').click(function (e) {
            if(selected) {
                var new_arg_tr_string = "<tr > <td>" + new_arg_query_id + "</td> <td>" + new_arg_query_display_name + "</td> <td> <span>" + new_arg_a + " </span><span> " + new_arg_op + "</span></td> <td><input value='" + new_arg_b + "'/></td> <td><input value=''/></td> <td><textarea rows='3' cols='50'/></td> </tr>";
                $('#selected-arguments-table tbody').append(new_arg_tr_string);

                // Update service arguments on backend
                update_service_arguments();
            }
            selected = false;
            $('#add_argument_popbtn').popover("hide");
        })
    });

});


// $(document).ready(function(){
//     $('#query-argument-select').select2();
// });
