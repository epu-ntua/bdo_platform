    // ******* csrftoken

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
    // ******* end csrftoken

    var service_id = get_service_id();
    var notebook_id = $('#notebook_id').val();
    var service_queries = JSON.parse('{}');


    function get_service_id() {
        return $('#service_id').val();
    }

    // Gather all the filter arguments that are exposed
    function gather_arguments() {
         exposed_args={'filter-arguments': [],'algorithm-arguments':[]};
        $("#selected-arguments-table1 tbody tr").each(
            function(index, elem){
                console.log($(this).text());
                var query_name = $(this).children().eq(1).text();
                exposed_args['filter-arguments'].push({
                    filter_a: $(this).children().eq(2).children().eq(0).text(),
                    filter_op: $(this).children().eq(2).children().eq(1).text(),
                    filter_b: $(this).children().eq(3).children().eq(0).val(),
                    query: query_name,
                    name: $(this).children().eq(4).text(),
                    title: $(this).children().eq(4).text(),
                    default: $(this).children().eq(3).text()
                });
                });
         $("#selected-arguments-table2 tbody tr").each(
            function(index, elem){
                exposed_args['algorithm-arguments'].push({
                    name: $(this).children().eq(0).text(),
                    title: $(this).children().eq(1).text(),
                    type: $(this).children().eq(2).text(),
                    description: $(this).children().eq(3).text(),
                });
                });

        return exposed_args;
    }

    function update_service_queries() {
        $.ajax({
            "type": "POST",
            "url": "/service_builder/update_service_queries/",
            "data": {
                service_id: service_id,
                selected_queries: JSON.stringify(service_queries)
            },
            "success": function(result) {
                console.log(result);
            },
            error: function (jqXHR) {
                alert('error');
            }
        });
    }

    function update_service_arguments() {
        var exposed_args = gather_arguments();
        // alert(JSON.stringify(exposed_args));
        $.ajax({
            "type": "POST",
            "url": "/service_builder/update_service_arguments/",
            "data": {
                service_id: service_id,
                exposed_args: JSON.stringify(exposed_args),
            },
            "success": function(result) {
                console.log(result);
            },
            error: function (jqXHR) {
                alert('error');
            }
        });
    }


    // Publish the service, update all service info
    $('#publish_service_btn').click(function (e) {
        var exposed_args = gather_arguments();
        togglemask(true);
        $.ajax({
            "type": "POST",
            "url": "/service_builder/publish/",
            "data": {
                notebook_id: notebook_id,
                selected_queries: JSON.stringify(service_queries),
                exposed_args: JSON.stringify(exposed_args),
                output_html: html_editor.getValue(),
                output_css: css_editor.getValue(),
                output_js: js_editor.getValue()
            },
            "success": function(result) {
                console.log(result);
                alert('Your service has been published successfully!');
                togglemask(false);
            },
            error: function (jqXHR) {
                alert('error');
                togglemask(false);
            }
        });
    });

