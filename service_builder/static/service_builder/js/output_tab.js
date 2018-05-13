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
            $('#outputIframe').attr("src", "/service_builder/service/"+service_id+"/");
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
            "src": 'http://localhost:8000/visualizations/get_line_chart_am/?y_var=i0_votemper&x_var=i0_time&query=1'});
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
	html_editor.setValue('<h1>Service 1</h1>');
	css_editor.setValue("h1 { color: blue; }\n" +
                        "iframe {width: 100%; height:300px;}");



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
                .attr("", v)
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

    $('#addVizModal select').on('change', function() {
        $('#addVizModal #viz_config').show();
        var new_query_id = $(this).children(":selected").attr("data-query-id");
        $('#addVizModal #selected_query').val(new_query_id);
        $('.popover').popover('hide');
          // updateVariables(this);
    });



    $(".viz_item").click(function (element) {
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
                    submit_conf(component_selector);
                    $(component_selector).popover("hide");
                });
            }
        });
    });


    var viz_request = "";
    function submit_conf(component_selector) {
        viz_request = "http://localhost:8000/visualizations/";
        viz_request += $('#addVizModal').find('.modal-body').find('#action').val();
        var conf_popover_id = '#' + $(component_selector).attr('aria-describedby');

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

        viz_request += '&query=' + $('#addVizModal #selected_query').val();

        show_viz(viz_request);
    }

    function show_viz(viz_request) {
        $("#viz_container").html('<iframe id="viz-iframe" ' +
            'src="'+viz_request+'" frameborder="0" allowfullscreen="" '+
            '></iframe>');
    }


    $("#addVizModal #submit-modal-btn").click(function () {
        $('#viz_container iframe').appendTo('#dynamic_dashboard');
        html_editor.replaceRange('\n<iframe src="'+viz_request+'" frameborder="0" allowfullscreen=""/>\n', {line: Infinity});
        html_editor.refresh();
        viz_request = "";
        $('#addVizModal #viz_container').empty();
    });
    $("#dismiss-modal-btn").click(function m (e) {
        viz_request = "";
        $('#addVizModal #viz_container').empty();
    });

