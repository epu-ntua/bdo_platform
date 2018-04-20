$(document).ready(function(){
    $("#query-select-container").hide();
    // How many queries are used from the service
    var number_of_queries = 0;
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
                var new_query_tr_string = "<tr> <td>" + new_query_id + "</td> <td>Q" + number_of_queries + "</td> <td>" + new_query_title + "</td> <td>" + new_query_document + "</td><td></td> </tr>";
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
