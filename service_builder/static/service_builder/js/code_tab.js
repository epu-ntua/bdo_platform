$(document).ready(function(){

      $(function () {
        $('[data-toggle="tooltip"]').tooltip()
      })
    // Popover to get a list of the queries to load
    $("#load_query_popbtn").popover({
        html: true,
        animation:true,
        trigger: 'manual',
        content: function() {
            return $('#load-query-select-container').html();
        }
    }).click(function(e) {
        $(this).popover('toggle');

        // Gather the queries as select options
        $('#load-query-select').empty();
        $('#load-query-select').append('<option disabled selected>-- select one of the queries to load --</option>');

        $('#selected-queries-table tbody tr').each(function( index ) {
            var query_id = $( this ).children().eq(0).text();
            var query_display_name = $( this ).children().eq(1).text();
            var query_name = $( this ).children().eq(2).text();
            $('#load-query-select').append('<option  data-query-id="'+query_id+'" data-display_name="'+query_display_name+'" title="' + query_display_name + '-' + query_name + '"> ' + query_display_name + '-' + query_name + ' </option>');
        });
        $('.popover-content #load-query-select').select2();


        // Get the selected query to load
        var load_query_id;
        var load_query_name;
        var selected = false;
        $('.popover-content #load-query-select').on('change', function() {
            selected = true;
            load_query_id = $(this).children(":selected").attr("data-query-id");
            load_query_name = $(this).children(":selected").attr("data-display_name");
        });



        // Load the query
        $('.popover-content #load_query_btn').click(function (e) {
            if (selected){
                // Gather the specific query arguments
                var exposed_args=[];
                $("#selected-arguments-table tbody tr").each(
                    function(index, elem){
                        if($(this).children().eq(1).text()==load_query_name){
                            console.log($(this).text());
                            exposed_args.push({
                                filter_a: $(this).children().eq(2).children().eq(0).text(),
                                filter_op: $(this).children().eq(2).children().eq(1).text(),
                                filter_b: $(this).children().eq(3).children().eq(0).val(),
                                query: load_query_name,
                                name: $(this).children().eq(4).children().eq(0).val(),
                                title: $(this).children().eq(4).children().eq(0).val(),
                                default: $(this).children().eq(3).children().eq(0).val()
                            });
                        }
                    }
                );
                // Make request to load the query
                $("#loading_div").removeClass("hidden");
                $.ajax({
                    "type": "POST",
                    "url": "/service_builder/load_query/",
                    "data": {
                        query_id: load_query_id,
                        query_name: load_query_name,
                        notebook_id: notebook_id,
                        exposed_args: JSON.stringify(exposed_args)
                    },
                    "success": function(result) {
                        alert("Query loaded in a Spark Dataframe with name: " + result[load_query_name]['dataframe']);
                        $("#loading_div").addClass("hidden");
                        console.log(result);

                        // Update the paragraphs info of the loaded query
                        service_queries[Object.keys(result)[0]]['paragraphs'].push(result[load_query_name]['paragraph']);
                        // Update query on the backend
                        update_service_queries();
                    },
                    error: function (jqXHR) {
                        alert('error');
                        $("#loading_div").addClass("hidden");
                    }
                });
            }
            selected = false;
            $('#load_query_popbtn').popover("hide");
        })
    });


    $("#save_dataframe_btn").click(function () {
        $("#saving_div").removeClass("hidden");
        var df_name = $("#df_name").val();
        $.ajax({
            "type": "POST",
            "url": "/service_builder/save_dataframe/",
            "data": {
                dataframe_name: df_name,
                notebook_id: notebook_id
            },
            "success": function(result) {
                alert("Successfully saved the selected dataframe!");
                console.log(result);
                $("#saving_div").addClass("hidden");
            },
            error: function (jqXHR) {
                alert('error');
                $("#saving_div").addClass("hidden");
            }
        });
    });


    // Popover to load saved dataframe
    $("#load_dataframe_popbtn").popover({
        html: true,
        animation:true,
        trigger: 'manual',
        content: function() {
            return $('#load-dataframe-select-container').html();
        }
    }).click(function(e) {
        $(this).popover('toggle');

        // Gather the queries as select options
        $('#load-dataframe-select').empty();
        $('#load-dataframe-select').append('<option disabled selected>-- select one of the saved dataframes to load --</option>');

        $('#selected-dataframes-table tbody tr').each(function( index ) {
            var dataframe_id = $( this ).children().eq(0).text();
            var dataframe_name = $( this ).children().eq(1).text();
            $('#load-dataframe-select').append('<option  data-dataframe-id="'+dataframe_id+'" data-dataframe-name="'+dataframe_name+'" > ' + dataframe_name + ' </option>');
        });
        $('.popover-content #load-dataframe-select').select2();

        // Get the selected query to load
        var load_dataframe_name;
        var selected = false;
        $('.popover-content #load-dataframe-select').on('change', function() {
            selected = true;
            load_dataframe_name = $(this).children(":selected").attr("data-dataframe-name");
        });

        // Load the query
        $('.popover-content #load_dataframe_btn').click(function (e) {
            if (selected){
                $("#loading_div").removeClass("hidden");
                // Make request to load the dataframe
                $.ajax({
                    "type": "POST",
                    "url": "/service_builder/load_dataframe/",
                    "data": {
                        dataframe_name: load_dataframe_name,
                        notebook_id: notebook_id
                    },
                    "success": function(result) {
                        alert("Query loaded in a Spark Dataframe with name: " + result[load_dataframe_name]['dataframe']);
                        console.log(result);
                        $("#loading_div").addClass("hidden");
                    },
                    error: function (jqXHR) {
                        alert('error');
                        $("#loading_div").addClass("hidden");
                    }
                });
            }
            selected = false;
            $('#load_dataframe_popbtn').popover("hide");
        })
    });
});
