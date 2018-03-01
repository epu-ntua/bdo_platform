$(document).ready(function(){
    var number_of_queries = 0;
    $("#add_query_popbtn").popover({
        html: true,
        animation:true,
        trigger: 'manual',
        content: function() {
            return $('#query-select-container').html();
        }
    }).click(function(e) {
        $(this).popover('toggle');

        $('.popover-content #query-select').select2();

        var new_query_id;
        var new_query_document;
        var new_query_title;
        var selected = false;
        $('.popover-content #query-select').on('change', function() {
            selected = true;
            new_query_id = $(this).children(":selected").attr("data-query-id");
            new_query_document = $(this).children(":selected").attr("data-query-document");
            new_query_title = $(this).children(":selected").attr("data-query-title");
            // alert(new_query_id);
            // alert(new_query_document);
            // var new_query_doc = $('#new_query_doc').val();
            // $('#myModal #selected_query').val(new_query_id);
            //   updateVariables(this);

        });


        $('.popover-content #add_new_query_btn').click(function (e) {
            if(selected) {
                number_of_queries++;
                var new_query_tr_string = "<tr> <td>" + new_query_id + "</td> <td>Q" + number_of_queries + "</td> <td>" + new_query_title + "</td> <td>" + new_query_document + "</td> </tr>";
                $('#selected-queries-table tbody').append(new_query_tr_string);
            }
            $('#add_query_popbtn').popover("hide");
        })
    });
});
