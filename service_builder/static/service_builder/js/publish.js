    var csrftoken = Cookies.get('csrftoken');
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });





    $('#publish_service_btn').click(function (e) {
        var notebook_id = $('#notebook_id').val();

        var selected_queries=[];
        $("#selected-queries-table tbody tr").each(
            function(index, elem){
                console.log($(this).text());
                selected_queries.push({
                    query_id: $(this).children().eq(0).text(),
                    display_name: $(this).children().eq(1).text()
                });
            }
        );

        var exposed_args={};
        $("#selected-arguments-table tbody tr").each(
            function(index, elem){
                console.log($(this).text());
                var query_id = $(this).children().eq(0).text();
                exposed_args[query_id]={
                    filter_a: $(this).children().eq(2).children().eq(0).text(),
                    filter_op: $(this).children().eq(2).children().eq(1).text(),
                    filter_b: $(this).children().eq(3).children().eq(0).val()
                };
            }
        );


        $.ajax({
            "type": "POST",
            "url": "/service_builder/publish/",
            "data": {
                notebook_id: notebook_id,
                selected_queries: JSON.stringify(selected_queries),
                exposed_args: JSON.stringify(exposed_args),
                output_html: html_editor.getValue(),
                output_css: css_editor.getValue(),
                output_js: js_editor.getValue()
            },
            "success": function(result) {
                console.log(result);
            },
            error: function (jqXHR) {
                alert('error');
            }
        });
    });

