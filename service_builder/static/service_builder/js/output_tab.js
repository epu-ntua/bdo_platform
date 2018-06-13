// Preview-Load service on the #output iframe
var preview_service = function () {
    $("#outputLoadImg").show();
    $.ajax({
        "type": "POST",
        "url": "/service_builder/update_service_output/",
        "data": {
            service_id: service_id,
            output_html: html_editor.getValue(),
            output_css: css_editor.getValue(),
            output_js: js_editor.getValue()
        },
        "success": function(result) {
            console.log(result);
            $('#outputIframe').attr("src", "/service_builder/service/"+service_id+"/preview/");
        },
        error: function (jqXHR) {
            alert('error');
        }
    });
};

$("#preview_btn").click(function () {
    preview_service();
});

// When preview button is clicked, load the created service
$("#outputIframe").on( "load", function(){
    show_hide_results();
    $(this).siblings("#outputLoadImg").css( "display", "none" );
});

$("#showServiceOutputChkbox").change(function(){
    show_hide_results();
});


function show_hide_results(){
    if ($("#showServiceOutputChkbox").is(':checked')) {
        $("#outputIframe").contents().find( "#service_result_container" ).show();
        $("#outputIframe").contents().find( "#service_result_container iframe" ).attr({
            // "src": 'http://localhost:8000/visualizations/get_line_chart_am/?y_var=i0_votemper&x_var=i0_time&query=1'
        });
    }
    else{
        $("#outputIframe").contents().find( "#service_result_container" ).hide();
    }
}

// ***************  CODE MIRROR  ***************
	// Base template
	var base_tpl =
			"<!doctype html>\n" +
			"<html>\n\t" +
      "<head>\n\t\t" +
      "<meta charset=\"utf-8\">\n\t\t" +
      "<title>Test</title>\n\n\t\t\n\t" +
      "<script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js\"></script>"+
      "</head>\n\t" +
      "<body>\n\t\n\t" +
      "</body>\n" +
      "</html>";

	var prepareSource = function() {
		var html = html_editor.getValue(),
            css = css_editor.getValue(),
			js = js_editor.getValue(),
			src = '';

		// HTML
		src = base_tpl.replace('</body>', html + '</body>');

		// CSS
		css = '<style>' + css + '</style>';
		src = src.replace('</head>', css + '</head>');

		// Javascript
		js = '<script> function get_service_id() { return window.parent.get_service_id()  } </script>' + js ;
        // js = '<script>' + js + '<\/script>';
		src = src.replace('</body>', js + '</body>');

		return src;
	};

	var render = function() {
		var source = prepareSource();

		var iframe = document.querySelector('#outputIframe'),
			iframe_doc = iframe.contentDocument;
		    // console.log(iframe_doc);

		iframe_doc.open();
		iframe_doc.write(source);
		iframe_doc.close();
	};

	// CM OPTIONS
	var cm_opt = {
		mode: 'text/html',
		gutter: true,
		lineNumbers: true,
        autoRefresh:true,
	};

	// HTML EDITOR
	var html_box = document.querySelector('#html textarea');
	var html_editor = CodeMirror.fromTextArea(html_box, cm_opt);

    // html_editor.on('change', function (inst, changes) {
    //     render();
    // });



	// CSS EDITOR
	cm_opt.mode = 'css';
	var css_box = document.querySelector('#css textarea');
	var css_editor = CodeMirror.fromTextArea(css_box, cm_opt);

    // css_editor.on('change', function (inst, changes) {
    //     render();
    // });

	// JAVASCRIPT EDITOR
	cm_opt.mode = 'javascript';
	var js_box = document.querySelector('#js textarea');
	var js_editor = CodeMirror.fromTextArea(js_box, cm_opt);

    // js_editor.on('change', function (inst, changes) {
    //     render();
    // });


	var cms = document.querySelectorAll('.CodeMirror');
	for (var i = 0; i < cms.length; i++) {

		cms[i].style.position = 'absolute';
		cms[i].style.top = '30px';
		cms[i].style.bottom = '0';
		cms[i].style.left = '0';
		cms[i].style.right = '0';
        cms[i].style.height = '60vh';
	}

	// SETTING CODE EDITORS INITIAL CONTENT
	html_editor.setValue('' +
        '<p>Give your service HTML here!</p>\n' +
        '<div id="service_args_container"></div>\n' +
        '<button class="btn-sm" id="submitServiceConfig">Submit</button>\n' +
        '<div id="service_result_container"></div>\n');
	css_editor.setValue("p { color: #30526a; }\n" +
                        "iframe {width: 100%; height:300px;}");
	js_editor.setValue("<script type='text/javascript'>" +
        "// Get form fields of all the service arguments\n" +
        "$(document).ready(function () {\n" +
        "   $.ajax({\n" +
        "       url: '/service_builder/load_service_args_form_fields/',\n" +
        "           data: {\n" +
        "           service_id: get_service_id()\n" +
        "       },\n" +
        "       type: 'GET',\n" +
        "       success: function(form_fields){\n" +
        "           $('#service_args_container').html(form_fields);\n" +
        "       }\n" +
        "   });\n" +
        "});\n" +
        " // Submit the service arguments \n" +
        "$(\"#submitServiceConfig\").click(function (element) { \n" +
        "   $.ajax({ \n" +
        "       url: '/service_builder/service/'+get_service_id()+'/execute/', \n" +
        "       data: $('#service_args_container').serialize(), \n" +
        "       type: 'GET', \n" +
        "       success: function(result){ \n" +
        "           $(\"#service_result_container\").html( result );\n" +
        "       },\n" +
        "        error: function () {\n" +
        "            alert('An error occured');\n" +
        "       }\n" +
        "   });\n" +
        "});\n" +
        "</script>\n" +
        "\n");



// ***************	END CODE MIRROR  ***************




// CODE FOR ADDING VISUALIZATION TO THE SERVICE (CHECK IT)
    $('#addVizModal').on('show.bs.modal', function () {
        $('#load-viz-query-select').empty();
        $('#load-viz-query-select').append('<option disabled selected>-- select one of the loaded queries --</option>');
        $('#selected-queries-table tbody tr').each(function( index ) {
            $('#load-viz-query-select').append('<option  data-query-id="'+$( this ).children().eq(0).text()+'"> ' + $( this ).children().eq(1).text() + '-' + $( this ).children().eq(2).text() +' </option>');
        });
    });


	$('#addVizModal select').select2();


    function updateVariables(element) {
        $('#addVizModal .variable-select').find('option').remove().end();
        $('#addVizModal .variable-select').append($("<option disabled selected>-- select variable --</option>"));
        var new_query_id = $('#addVizModal #selected_query').val();
        var new_query_doc = {};
        $.ajax({
            url: '/queries/get_query_variables/',
            data: {
                id: new_query_id,
                document: new_query_doc
                },
            type: 'GET',
            success: function(result){
                var variables = result['variables'];
                var dimensions = result['dimensions'];
                $('.variable-select').append($("<option></option>")
                .attr("value", '')
                .text('-- column select --'));

                $.each(variables, function(k, v) {
                    $('#addVizModal .variable-select').append($("<option></option>")
                        .attr("value", v)
                        .text(k));
                });

                $.each(dimensions, function(k, v) {
                    $('#addVizModal .variable-select').append($("<option></option>")
                        .attr("value", v)
                        .text(k));
                });
            }
        });
    }


    $('#addVizModal .select2').on("click", function() {
        $('.popover').popover('hide');
    });

    $('#addVizModal #query select').on('change', function() {
        $('#addVizModal #query #viz_config').show();
        var new_query_id = $(this).children(":selected").attr("data-query-id");
        $('#addVizModal #query #selected_query').val(new_query_id);
        $('.popover').popover('hide');
          updateVariables(this);
    });

    $('#addVizModal #dataframe #selected_dataframe').on('change', function() {
        $('#addVizModal #dataframe #viz_config').show();
        var new_query_id = $(this).children(":selected").attr("data-query-id");
        $('#addVizModal #selected_query').val(new_query_id);
        $('.popover').popover('hide');
          // updateVariables(this);
    });



    $("#query .viz_item").click(function (element) {
      var component_id = $(this).attr('data-viz-id');
      var component_selector = 'li[data-viz-id="'+component_id+'"]';
      $.ajax({
            url: '/dashboards/get_visualization_form_fields',
            data: {
                id: parseInt(component_id),
                order: 1
                },
            type: 'GET',
            success: function(form_fields){
                $("#conf-container").html(form_fields);
                $("#conf-container").append('<button type="button" id="select_conf_ok" class="btn btn-sm btn-success" data-toggle="popover">OK</button>');

                $(component_selector).popover({
                    html: true,
                    title: 'Configure visualisation',
                    trigger: 'manual',
                    content: function() {
                        return $('#conf-container').html();
                    }
                });
                updateVariables($('#load-viz-query-select'));
                $(component_selector).popover('toggle');
                var popver_id = '#' + $(component_selector).attr('aria-describedby');
                $(popver_id+' #select_conf_ok').click(function(e){
                    submit_conf(component_selector, 'query');
                    $(component_selector).popover("hide");
                });
            }
        });
    });

    $("#dataframe .viz_item").click(function (element) {
      var component_id = $(this).attr('data-viz-id');
      var component_selector = '#dataframe li[data-viz-id="'+component_id+'"]';
      $.ajax({
            url: '/dashboards/get_visualization_form_fields_df',
            data: {
                id: parseInt(component_id),
                order: 1
                },
            type: 'GET',
            success: function(form_fields){
                $("#conf-container").html(form_fields);
                $("#conf-container").append('<button type="button" id="select_conf_ok" class="btn btn-sm btn-success" data-toggle="popover">OK</button>');

                $(component_selector).popover({
                    html: true,
                    title: 'Configure visualisation',
                    trigger: 'manual',
                    content: function() {
                        return $('#conf-container').html();
                    }
                });
                $(component_selector).popover('toggle');
                // alert("submit conf");
                var popver_id = '#' + $(component_selector).attr('aria-describedby');
                $(popver_id+' #select_conf_ok').click(function(e){
                    // alert("submit conf");
                    submit_conf(component_selector, 'df');
                    $(component_selector).popover("hide");
                });
            }
        });
    });


    var viz_request = "";
    function submit_conf(component_selector, from) {
        // viz_request = "http://localhost:8000/visualizations/";
        viz_request = "/visualizations/";
        viz_request += $('#addVizModal').find('.modal-body').find('#action').val();
        var conf_popover_id = '#' + $(component_selector).attr('aria-describedby');
        // alert(viz_request);
        var submitted_args = $('#addVizModal').find(conf_popover_id).find('.popover-content').clone();
        var selects = $('#addVizModal').find(conf_popover_id).find('.popover-content').find("select");
        $(selects).each(function(i) {
            var select = this;
            $(submitted_args).find("select").eq(i).val($(select).val());
        });
        $('#config-viz-form').empty();
        $('#config-viz-form').append(submitted_args);


        var myData = $("#config-viz-form").serialize();
        viz_request += '?';
        viz_request += myData;

        if (from === 'query')
            viz_request += '&query=' + $('#addVizModal #selected_query').val();
        else
            viz_request += '&df=' + $('#addVizModal #selected_dataframe').val();
            viz_request += '&notebook_id=' + $('#notebook_id').val();
        // alert(viz_request);
        show_viz(viz_request, from);
    }

    function show_viz(viz_request, from) {
        if (from === 'query')
            $("#query #viz_container").html('<iframe id="viz-iframe" ' +
                'src="'+viz_request+'" frameborder="0" allowfullscreen="" '+
                '></iframe>');
        else
            $("#dataframe #viz_container").html('<iframe id="viz-iframe" ' +
                'src="'+viz_request+'" frameborder="0" allowfullscreen="" '+
                '></iframe>');
    }


    $("#addVizModal #submit-query-btn").click(function () {
        $('#query #viz_container iframe').appendTo('#dynamic_dashboard');
        html_editor.replaceRange('\n<div id="viz_container"><div class="loadingFrame"><img src="http://assets.motherjones.com/interactives/projects/features/koch-network/shell19/img/loading.gif"/></div><iframe src="'+viz_request+'" frameborder="0" allowfullscreen="" style="width: 100%;min-height: 500px;"></iframe></div>\n', {line: Infinity});
        html_editor.refresh();
        viz_request = "";
        $('#query #addVizModal #viz_container').empty();
    });

    $("#addVizModal #submit-dataframe-btn").click(function () {
        $('#dataframe #viz_container iframe').appendTo('#dynamic_dashboard');
        html_editor.replaceRange('\n<div class="viz_container row"><div class="loadingFrame"><img src="http://assets.motherjones.com/interactives/projects/features/koch-network/shell19/img/loading.gif"/></div><iframe src="'+viz_request+'" frameborder="0" allowfullscreen="" style="width: 100%;min-height: 500px;"></iframe></div>\n', {line: Infinity});
        html_editor.refresh();
        viz_request = "";
        $('#dataframe #addVizModal #viz_container').empty();
    });

    $("#dismiss-modal-btn").click(function m (e) {
        viz_request = "";
        $('#addVizModal #viz_container').empty();
    });

    $("#queryPill").click(function () {
        $("#addVizModal #submit-dataframe-btn").hide();
        $("#addVizModal #submit-query-btn").show();
    });

    $("#dataframePill").click(function () {
        $("#addVizModal #submit-dataframe-btn").show();
        $("#addVizModal #submit-query-btn").hide();
    });
