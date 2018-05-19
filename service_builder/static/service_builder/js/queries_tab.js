$(document).ready(function(){
     $.ajax({
            "type": "POST",
            "url": "/service_builder/run_initial_zep_paragraph/",
            "data": {
                service_id: get_service_id()
            },
            "success": function(result) {
                console.log(result);
            },
            error: function (jqXHR) {
                alert('error');
            }
        });


    $("#query-select-container").hide();
    // How many queries are used from the service
    var number_of_queries = 0;

      $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })


    $("#add_query_popbtn").popover({
        html: true,
        animation:true,
        trigger: 'manual',
        content: function() {
            return $('#query-select-container').html();
        }
    }).click(function(e) {
        // Show popover
        $(this).popover('toggle');
        // Use select2
        $('.popover-content #query-select').select2();

        // Get the info of the new selected query
        var new_query_id;
        var new_query_document;
        var new_query_title;
        var selected = false;
        $('.popover-content #query-select').on('change', function() {
            selected = true;
            new_query_id = $(this).children(":selected").attr("data-query-id");
            new_query_document = $(this).children(":selected").attr("data-query-document");
            new_query_title = $(this).children(":selected").attr("data-query-title");
        });

        // Add the selected query to the list
        $('.popover-content #add_new_query_btn').click(function (e) {
            if(selected) {
                number_of_queries++;
                // var new_query_tr_string = "<tr> <td data-columnname='query_id'>" + new_query_id + "</td> <td data-columnname='number'>Q" + number_of_queries + "</td> <td data-columnname='title'>" + new_query_title + "</td> <td data-columnname='doc'>" + new_query_document + "</td><td></td> </tr>";
                var new_query_tr_string = "<tr> <td data-columnname='query_id'>" + new_query_id + "</td> <td data-columnname='number'>Q" + number_of_queries + "</td> <td data-columnname='title'>" + new_query_title + "</td> <td data-columnname='doc' style='display: none;'>" + new_query_document + "</td><td></td> </tr>";
                $('#selected-queries-table tbody').append(new_query_tr_string);

                // Add the query to the Object that stores all the selected queries
                service_queries["Q" + String(number_of_queries)] = {'query_id': new_query_id, 'paragraphs': []};
                // Update the service queries on the backend
                update_service_queries();
            }
            selected = false;
            $('#add_query_popbtn').popover("hide");
        })
    });
});
