$(document).ready(function(){
    $("#query_template_popbtn").popover({
        html: true,
        animation:true,
        trigger: 'manual',
        content: function() {
            return $('#query-select-container').html();
        }
    }).click(function(e) {
        $(this).popover('toggle');
        var new_query_id;
        var new_query_document;
        var new_query_title;
        $('.popover-content #query-select').on('change', function() {
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
            var new_query_tr_string = "<tr> <td>"+new_query_id+"</td> <td>"+new_query_title+"</td> <td>"+new_query_document+"</td> </tr>";
            $('#selected-queries-table tbody').append(new_query_tr_string);
            $('#query_template_popbtn').popover("hide");
        })
    });
});
